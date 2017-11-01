from __future__ import absolute_import

from pprint import pprint
import json
import base
import db
import wsgi
import re
import random

with open('image-list.json') as data_file:
    fulldata = json.load(data_file)

# remove 'info' key and value


def clean_data(data):
    for k in data:
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


def make_span(prettier_data):
    span_data = {}
    for k in prettier_data:
        nodes = prettier_data[k]
        span_data.setdefault(k, {})
        if 'start' in nodes[0]['name']:
            span_data[k]['starttime'] = float(nodes[0]['timestamp'].rsplit(
                ':', 2)[2]) + float(nodes[0]['timestamp'].rsplit(':', 2)[1]) * 60
        else:
            span_data[k]['starttime'] = float(nodes[1]['timestamp'].rsplit(
                ':', 2)[2]) + float(nodes[1]['timestamp'].rsplit(':', 2)[1]) * 60
        span_data[k]['base_id'] = nodes[0]['base_id']
        span_data[k]['trace_id'] = nodes[0]['trace_id']
        span_data[k]['project'] = nodes[0]['project']
        span_data[k]['name'] = re.sub(
            '-start', '', re.sub('-stop', '', nodes[0]['name']))
        span_data[k]['parent_id'] = nodes[0]['parent_id']
        span_data[k]['service'] = nodes[0]['service']
        span_data[k]['time'] = abs(float(nodes[0]['timestamp'].rsplit(':', 2)[2])
                                   + float(nodes[0]['timestamp'].rsplit(':', 2)[1]) * 60
                                   - float(nodes[1]['timestamp'].rsplit(':', 2)[2])
                                   - float(nodes[1]['timestamp'].rsplit(':', 2)[1]) * 60)
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
class_data = {}


def set_class(tree):
    if not tree:
        return
    if not isinstance(tree, dict):
        for node in tree:
            if node.get('name') == 'db':
                class_data[node['trace_id']] = db.DB(node['project'], node['service'], node[
                                                   'level'], node['trace_id'], node['parent_id'])
            elif node.get('name') == 'wsgi':
                class_data[node['trace_id']] = wsgi.WSGI(node['project'], node['service'], node[
                                                    'level'], node['trace_id'], node['parent_id'])
            if node.get('children'):
                set_class(node['children'])
    else:
        if not tree.get('name'):
            class_data[tree['trace_id']] = base.Base(trace_id=tree['trace_id'], level=tree['level'])
        elif tree.get('name') == 'db':
            class_data[tree['trace_id']] = db.DB(tree['project'], tree['service'], tree[
                                               'level'], tree['trace_id'], tree['parent_id'])
        elif tree.get('name') == 'wsgi':
            class_data[tree['trace_id']] = wsgi.WSGI(tree['project'], tree['service'], tree[
                                                'level'], tree['trace_id'], tree['parent_id'])
        set_class(tree['children'])

#### put instances to instance.nodes

def gather_instance(class_data):
    for key in class_data:
        node = class_data[key]
        for k in class_data:
            n = class_data[k]
            if n.parent_id == node.trace_id:
                node.append(n)


cleaned_data = clean_data(fulldata)
better_data = make_prettier_data(cleaned_data)
span_data = make_span(better_data)
tree = build_tree(span_data)
add_depth(tree)
rearrange_tree(tree)
set_class(tree)
gather_instance(class_data)
class_data['a4a8cdea-09cd-45a8-b875-d357d14151ef'].create_signature(class_data['a4a8cdea-09cd-45a8-b875-d357d14151ef'].nodes)
pprint(class_data['a4a8cdea-09cd-45a8-b875-d357d14151ef'].signature)







