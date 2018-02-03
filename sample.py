from __future__ import absolute_import
from __future__ import print_function
from pprint import pprint
import json
import re
import random
import math
import sys
from datetime import datetime

import base
import db
import wsgi
import compute
import driver
import neutron
import rpc
import volume
import vif_driver
import stack
import nova

timefmt = '%Y-%m-%dT%H:%M:%S.%f'

if len(sys.argv) != 2:
    print('Invalid command!\n\ttry again with: python sample.py [json file]')
    exit()
with open(sys.argv[1]) as data_file:
    fulldata = json.load(data_file)

# remove 'info' key and value

info_data = {}

def clean_data(data):
    global info_data
    for k in data:
        if k['name'].endswith('start'):
            info_data[k['trace_id']] = k['info']
        del k['info']
    return data

# gather 2 nodes together


def make_prettier_data(cleaned_data):
    new_data = {}
    for node in cleaned_data:
        if node['trace_id'] in new_data:
            new_data[node['trace_id']].append(node)
        else:
            new_data.setdefault(node['trace_id'], [])
            new_data[node['trace_id']] = [node]
    return new_data

# make span from prettier data

def msec(dt):
    microsec = (dt.microsecond + (dt.second + dt.day * 24 * 3600) * 1e6)
    return int(microsec / 1000.0)



def make_span(prettier_data):
    span_data = {}
    for k in prettier_data:
        nodes = prettier_data[k]
        span_data.setdefault(k, {})

        if nodes[0]['name'].endswith('start'):
            span_data[k]['starttime'] = msec(datetime.strptime(nodes[0]['timestamp'], timefmt))
            span_data[k]['finishtime'] = msec(datetime.strptime(nodes[1]['timestamp'], timefmt))
            span_data[k]['timestamp'] = nodes[0]['timestamp']
        else:
            span_data[k]['starttime'] = msec(datetime.strptime(nodes[1]['timestamp'], timefmt))
            span_data[k]['finishtime'] = msec(datetime.strptime(nodes[0]['timestamp'], timefmt))
            span_data[k]['timestamp'] = nodes[1]['timestamp']

        span_data[k]['base_id'] = nodes[0]['base_id']
        span_data[k]['trace_id'] = nodes[0]['trace_id']
        span_data[k]['project'] = nodes[0]['project']
        span_data[k]['name'] = nodes[0]['name'].split('-')[0]
        span_data[k]['parent_id'] = nodes[0]['parent_id']
        span_data[k]['service'] = nodes[0]['service']
        span_data[k]['time'] = span_data[k]['finishtime'] - span_data[k]['starttime']
        
    return span_data

# build tree from data


def build_tree(data):
    tree = {}
    randomkey = random.choice(data.keys())
    tree['trace_id'] = data.get(randomkey)['base_id']
    tree.setdefault('children', [])
    for k in data:
        node = data[k]
        parent_id = node['parent_id']
        if parent_id in data:
            data[parent_id].setdefault('children', [])
            data[parent_id]["children"].append(node)
        else:
            tree['children'].append(node)
    return tree

# add depth to tree


def add_depth(tree, depth=0):
    if not tree:
        return
    if isinstance(tree, dict):
        tree['level'] = depth
        add_depth(tree['children'], depth + 1)
    else:
        for node in tree:
            node['level'] = depth
            if node.get('children'):
                add_depth(node['children'], depth + 1)

# rearrange tree to correct time


def rearrange_tree(data):
    if not data:
        return
    if isinstance(data, list):
        newdata = sorted(data, key=lambda k: k['starttime'])
        for i in range(len(data)):
            data[i] = newdata[i]
        for node in data:
            if node.get('children'):
                rearrange_tree(node['children'])
    else:
        rearrange_tree(data['children'])

# set class for nodes in tree

queue = []

def put_queue(tree):
    global queue
    if not tree:
        return
    if isinstance(tree, list):
        for node in tree:
            queue.append(node)
            if node.get('children'):
                put_queue(node['children'])
    else:
        queue.append(tree)
        if tree.get('children'):
            put_queue(tree['children'])

class_data = []

def set_class(queue):
    global class_data
    for node in queue:
        if not node.get('name'):
            class_data.append(base.Base(trace_id=node['trace_id'], level=node['level']))
        elif node.get('name') == 'db':
            class_data.append(db.DB(node['project'], node['service'], 
                node['level'], node['trace_id'], node['parent_id'], node['starttime'], node['time']))
        elif node.get('name') == 'wsgi':
            class_data.append(wsgi.WSGI(node['project'], node['service'], 
                node['level'], node['trace_id'], node['parent_id'], node['starttime'], node['time']))
        elif node.get('name') == 'compute_api':
            class_data.append(compute.compute(node['project'], node['service'], 
                node['level'], node['trace_id'], node['parent_id'], node['starttime'], node['time']))
        elif node.get('name') == 'rpc':
            class_data.append(rpc.RPC(node['project'], node['service'], 
                node['level'], node['trace_id'], node['parent_id'], node['starttime'], node['time']))
        elif node.get('name') == 'driver':
            class_data.append(driver.driver(node['project'], node['service'], 
                node['level'], node['trace_id'], node['parent_id'], node['starttime'], node['time']))
        elif node.get('name') == 'vif_driver':
            class_data.append(vif_driver.vif(node['project'], node['service'], 
                node['level'], node['trace_id'], node['parent_id'], node['starttime'], node['time']))
        elif node.get('name') == 'neutron_api':
            class_data.append(neutron.neutron(node['project'], node['service'], 
                node['level'], node['trace_id'], node['parent_id'], node['starttime'], node['time']))
        elif node.get('name') == 'volume_api':
            class_data.append(volume.volume(node['project'], node['service'], 
                node['level'], node['trace_id'], node['parent_id'], node['starttime'], node['time']))
        elif node.get('name') == 'nova_image':
            class_data.append(nova.nova(node['project'], node['service'], 
                node['level'], node['trace_id'], node['parent_id'], node['starttime'], node['time']))
        else:
            class_data.append(stack.stack(node['project'], node['service'], 
                node['level'], node['trace_id'], node['parent_id'], node['starttime'], node['time']))

#### put instances to instance.nodes

def gather_instance(class_data):
    for node in class_data:
        for n in class_data:
            if n.parent_id == node.trace_id:
                node.append(n)


cleaned_data = clean_data(fulldata)
better_data = make_prettier_data(cleaned_data)
span_data = make_span(better_data)
tree = build_tree(span_data)
add_depth(tree)
rearrange_tree(tree)
put_queue(tree)
set_class(queue)
gather_instance(class_data)

##########################################################

start = 999999999.99
stop = 0.0

def get_start_stop_time(tree):
    global start, stop
    if not tree:
        return 
    if isinstance(tree, list):
        for node in tree:
            get_start_stop_time(node)
    else:
        if not tree.get('name'):
            get_start_stop_time(tree['children'])
        else:
            node_start = tree['starttime']
            node_stop = tree['finishtime']
            if start >= node_start:
                start = node_start
            if node_stop >= stop:
                stop = node_stop
            if tree.get('children'):
                get_start_stop_time(tree['children'])

get_start_stop_time(tree)

maxrange = 150

def visualize_trace(tree):
    global start, stop
    if not tree:
        return
    if isinstance(tree, list):
        for node in tree:
            visualize_trace(node)
    else:
        if not tree.get('name'):
            print('%-20s' % 'base', end='')
            print('[', end='')
            for i in range(maxrange + 1):
                print('-', end = '')
            print(']')
            visualize_trace(tree['children'])
        else:
            print('%-20s' % (tree['name'] + str(tree['level'])), end='')
            for i in range(int(math.ceil((tree['starttime'] - start) * maxrange / (stop - start)))):
                print(' ', end = '')
            print('[', end='')
            for i in range(int(math.ceil(tree['time'] * maxrange / (stop - start)))):
                print('-', end = '')
            print(']')
            if tree.get('children'):
                visualize_trace(tree['children'])

def draw_tree(signature):
    print('|-base')
    for node in signature:
        level = int(re.search(r'\d+', node).group())
        print('|-', end='')
        for i in range(level):
            print('----', end='')
        print(node)

info_extract = {}
data_extract = {}

def generate_processed_data():
    i = []
    dt = []
    root = []
    global info_extract, data_extract

    for obj in class_data:
        if type(obj) == base.Base:
            obj.create_signature(obj.nodes)
            signature = '.'.join(obj.signature)
            obj.return_children(root, obj.nodes)
    for node in root:
        for d in info_data:
            if node.trace_id == d:
                i.append(info_data[d])
        for d in span_data:  
            if node.trace_id == span_data[d]['trace_id']:
                tmp = {
                    'name' : node.class_name,
                    'service' : node.service,
                    'project' : node.project,
                    'starttime' : span_data[d]['timestamp'],
                    'duration' : node.duration,
                    'parent_id' : node.parent_id,
                    'base_id' : span_data[d]['base_id']
                }
                dt.append(tmp)
    info_extract[signature] = i
    data_extract[signature] = dt
    with open('_'.join([sys.argv[1].split('.')[0], 'info.json']), 'w+') as info:
        json.dump(info_extract, info, indent=4)
    with open('_'.join([sys.argv[1].split('.')[0], 'data.json']), 'w+') as data:
        json.dump(data_extract, data, indent=4)

sub = {}

def create_subworkflow():
    global sub
    subcount = 0
    for obj in class_data:
        obj.create_signature(obj.nodes)
        for i in xrange(3, 10):
            flag = 0
            if len(obj.signature) == i:
                substring = ''.join(i for i in '.'.join(obj.signature) if not i.isdigit())
                for k, v in sub.iteritems():
                    if substring == v:
                        flag = 1
                if flag == 0:
                    sub[subcount] = substring
                    subcount = subcount + 1
    with open('_'.join([sys.argv[1].split('.')[0], 'sub.json']), 'w+') as subfile:
        json.dump(sub, subfile, indent = 4)

def replace_subworkflow():
    for obj in class_data:
        if type(obj) == base.Base:
            obj.create_signature(obj.nodes)
            signature = ''.join(i for i in '.'.join(obj.signature) if not i.isdigit())
    for k, v in sub.iteritems():
        signature = signature.replace(v, 'sub' + str(k))
        
    pprint(signature)


while(1):
    print('\n\n1. Print signature')
    print('2. Visualize trace')
    print('3. Draw tree')
    print('4. Extract files')
    print('5. Signature after combining workflow')
    decide = raw_input("Option: ")
    if int(decide) == 2:
        visualize_trace(tree)
    elif int(decide) == 1:
        for obj in class_data:
            if type(obj) == base.Base:
                obj.create_signature(obj.nodes)
                print('.'.join(obj.signature))
    elif int(decide) == 3:
        for obj in class_data:
            if type(obj) == base.Base:
                obj.create_signature(obj.nodes)
                draw_tree(obj.signature)
    elif int(decide) == 4:
        generate_processed_data()
    elif int(decide) == 5:
        create_subworkflow()
        replace_subworkflow()
    else:
        exit()

