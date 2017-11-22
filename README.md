# tracing-simple
1. clean_data: remove 'info' in dataset 
2. make_prettier_data: gather 2 nodes having the same trace_id together
3. make_span: combine 2 nodes to 1 span, calculate span starting time and duration
4. build_tree: build a tree after making span
5. add_depth: add a number at each tree level
6. rearrange_tree: reorder span tree 
7. set_class: set_class for tree nodes
8. gather_instance: put children spans to nodes variable in parent span instance
