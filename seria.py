import logging
import re

__author__ = 'Max'
__version__ = '0.2.1'

ATTRIBUTE_PATTERN = r'([a-zA-Z][0-9a-zA-Z.:_]*)'
VALUE_PATTERN = r'(.*)'

# logging.basicConfig(level=logging.DEBUG)


class alist:
    '''Association list that maintains the order of key-value pairs and allows insertion.
    The dict part is used to store the data, while the list part is used to store the order of insertion.'''

    def __init__(self, data: dict = None):
        self.data = data or dict()
        self.order = list(data.keys())

    def __iter__(self):
        for key in self.order:
            yield key, self.get(key)

    def __contains__(self, key) -> bool:
        return key in self.keys()

    # list operations

    def index(self, key) -> int:
        return self.order.index(key)

    def insert(self, index, key, value):
        self.data[key] = value
        self.order.insert(index, key)

    def remove(self, key):
        del self.data[key]
        self.order.remove(key)

    # dict operations

    def get(self, key):
        return self.data.get(key)

    def keys(self):
        return set(self.order)

    def put(self, key, value):
        self.data[key] = value
        if key not in self.order:
            self.order.append(key)


class SeriaNode:
    def __init__(self, header: str, classname: str):
        self.header = header
        self.data_group = list()
        self.data_group.append(alist({'m_classname': classname}))

    def _add_attribute(self, name: str, value: str):
        last_group = self.data_group[-1]
        if not isinstance(last_group, alist):
            self.data_group.append(alist({name: value}))
        else:
            if name in last_group:
                existing_value = last_group.get(name)
                if isinstance(existing_value, list):
                    last_group.put(name, existing_value + [value])
                else:
                    last_group.put(name, [existing_value, value])
            else:
                last_group.put(name, value)

    def _add_child(self, node):
        if not isinstance(node, SeriaNode):
            raise TypeError('Child must be a SeriaNode')
        self.data_group.append(node)

    # attribute read operations

    def get_attribute(self, name: str):
        '''Get attribute value if the current node.'''

        for group in self.data_group:
            if isinstance(group, alist):
                # assume that attribute only appear in consecutive order and will not spread accross groups
                if name in group.keys():
                    return group.get(name)

        return None

    def get_attributes(self):
        '''Get all attributes in the current node.'''

        attributes = dict()

        for group in self.data_group:
            if isinstance(group, alist):
                for name, value in group:
                    attributes[name] = value

        return attributes

    def has_attribute(self, name: str) -> bool:
        '''Check if the current node has an attribute.'''

        for group in self.data_group:
            if isinstance(group, alist):
                if name in group.keys():
                    return True

        return False

    def attribute_names(self) -> set:
        '''Get all attribute names in the current node.'''

        names = set()

        for group in self.data_group:
            if isinstance(group, alist):
                names = names.union(group.keys())

        return names

    # attribute write operations

    def set_attribute(self, name: str, value: str):
        '''Set an attribute value in the current node. This works for both new and existing attributes.
        New attribute will be add to the end of the current node. If the last section is a node, It will be add after the node.
        A real example is the root node of the profile, which contains sections of attribute that spread accross the file.'''

        # existing attribute will be replaced with new value
        for group in self.data_group:
            if isinstance(group, alist):
                if name in group.keys():
                    group.put(name, value)
                    return

        # new attribute will be add to the end of the current node
        self._add_attribute(name, value)

    def update_attribute(self, name: str, value: str):
        '''Update the attribute value of the root node.
        It will also find and update the attribute in the child that reference the previous value.
        This is different from set_attribute, which only update existing attribute.'''

        old_value = self.get_attribute(name)
        if old_value is None or old_value == value:
            return

        for group in self.data_group:
            if isinstance(group, alist):
                if name in group.keys():
                    group.put(name, value)

        for group in self.data_group:
            if isinstance(group, SeriaNode):
                group.update_attribute_by_value(old_value, value)

    def update_attribute_by_value(self, old_value: str, new_value: str):
        '''Update the attribute value by its old value. This applies to all child nodes and recursively.
        If the attribute value is equal to the old value, it will be updated to the new value.'''

        for group in self.data_group:
            if isinstance(group, alist):
                for name, value in group:
                    if value == old_value:
                        group.put(name, new_value)
            else:
                group.update_attribute_by_value(old_value, new_value)

    def put_attribute_before(self, name: str, value: str, before: str):
        '''Add an attribute before another attribute.
        @param name: the name of the attribute to add.
        @param value: the value of the attribute to add.
        @param before: the name of the attribute before which the new attribute will be added.'''

        if self.has_attribute(name):
            self.set_attribute(name, value)
            return

        for group in self.data_group:
            if isinstance(group, alist):
                if before in group.keys():
                    index = group.index(before)

                    group.insert(index, name, value)
                    return

    def put_attribute_after(self, name: str, value: str, after: str):
        '''Add an attribute after another attribute.
        @param name: the name of the attribute to add.
        @param value: the value of the attribute to add.
        @param after: the name of the attribute after which the new attribute will be added.'''

        if self.has_attribute(name):
            self.set_attribute(name, value)
            return

        for group in self.data_group:
            if isinstance(group, alist):
                if after in group.keys():
                    index = group.index(after)

                    group.insert(index + 1, name, value)
                    return

    def del_attribute(self, name: str):
        '''Delete an attribute from the current node.
        @param name: the name of the attribute to delete.'''

        for group in self.data_group:
            if isinstance(group, alist):
                if name in group.keys():
                    group.remove(name)
                    return

    # node read operations

    def get_node(self, index: int):
        '''Get a child node by its order (index) in the file.'''

        return self.get_nodes()[index]

    def get_node_if(self, predicate):
        '''Get the first child node that satisfies the predicate function.'''

        for group in self.data_group:
            if isinstance(group, SeriaNode):
                if predicate(group):
                    return group

        return None

    def get_node_by_class(self, classname: str):
        '''Get the first child node with the specified class name.'''

        return self.get_node_if(lambda node: node.get_attribute('m_classname') == classname)

    def get_nodes(self) -> list:
        '''Get all direct child nodes of the current node.
        @return: a list of child nodes.'''

        return [group for group in self.data_group if isinstance(group, SeriaNode)]

    def get_nodes_by_class(self, classname: str) -> list:
        '''Get all child nodes with the specified class name.
        @return: a list of child nodes'''

        return self.filter_nodes(lambda node: node.get_attribute('m_classname') == classname)

    def node_classes(self) -> set:
        '''Get all classnames of child nodes.
        @return: a set of classnames.'''

        return set(node.get_attribute('m_classname') for node in self.get_nodes())

    def node_count(self) -> int:
        '''Get the number of child nodes.'''

        return len(self.get_nodes())

    def node_index(self, node) -> int:
        '''Get the order (index) of a child node.'''

        return self.get_nodes().index(node)

    # node write operations

    def add_node(self, node):
        '''Add a child node to the end of the current node.'''

        self.data_group.append(node)

    def put_node_before(self, node, before):
        '''Add a child node before another child node.'''

        self.data_group.insert(self.data_group.index(before), node)

    def put_node_after(self, node, after):
        '''Add a child node after another child node.'''

        self.data_group.insert(self.data_group.index(after) + 1, node)

    def put_node_before_index(self, node, index):
        '''Add a child node before another child node by index.'''

        self.put_node_before(node, self.get_node(index))

    def put_node_after_index(self, node, index):
        '''Add a child node after another child node by index.'''

        self.put_node_after(node, self.get_node(index))

    def del_node(self, node):
        '''Delete a child node (by reference object) from the current node.'''

        self.data_group.remove(node)

    # stream-like operations

    def foreach_node(self, action):
        '''Apply an action function to all child nodes.'''

        for group in self.data_group:
            if isinstance(group, SeriaNode):
                action(group)

    def filter_nodes(self, predicate) -> list:
        '''Filter all child nodes with a predicate function.
        @return: a list of child nodes that satisfy the predicate.'''

        return [node for node in self.get_nodes() if predicate(node)]

    def map_nodes(self, mapper) -> list:
        '''Map all child nodes with a mapper function.
        @return: a list of mapped values.'''

        return [mapper(node) for node in self.get_nodes()]


def _match_attribute(input: str):
    '''Match an attribute and its value from a line of text.
    @return: a tuple of the attribute and its value, or None if no match.'''

    match_result = re.match(ATTRIBUTE_PATTERN + '=' + VALUE_PATTERN, input)
    if match_result:
        return match_result.group(1), match_result.group(2)
    return None, None


def tree(node: SeriaNode, max_depth: int = None) -> str:
    '''Print a SeriaNode in a tree-like format.'''

    logger = logging.getLogger('seria.tree')

    if max_depth is not None and max_depth < 1:
        logger.error('max_depth must be greater or equal to 1')

    output = []

    def _print_node(node, depth):
        output.append('  ' * (depth - 1) + node.get_attribute('m_classname'))

        if max_depth is None or depth < max_depth:
            for child in node.get_nodes():
                _print_node(child, depth + 1)

    _print_node(node, 1)

    return '\n'.join(output)


def dump_str(node: SeriaNode) -> str:
    '''Dump a SeriaNode to a string.'''

    output = []

    if node.header is not None:
        output.append(node.header)
    output.append('{')

    for group in node.data_group:
        if isinstance(group, alist):
            for name, value in group:
                if name == '_mesh':
                    output.extend(f'{v}' for v in value)
                else:
                    if isinstance(value, list):
                        output.extend(f'{name}={v}' for v in value)
                    else:
                        output.append(f'{name}={value}')
        else:
            output.append(dump_str(group))

    output.append('}')
    return '\n'.join(output)


def dump(node: SeriaNode, filepath: str):
    '''Dump a SeriaNode to a file.'''

    logger = logging.getLogger('seria.dump')

    try:
        with open(filepath, 'w', encoding='cp1251') as file:
            file.write(dump_str(node) + '\n')
    except IOError:
        logger.error(f'Could not open file: {filepath}')


def load(filepath: str) -> SeriaNode:
    '''Load a SeriaNode from a file.
    @return: the root node of the SeriaNode, or None if the file could not be opened.'''

    logger = logging.getLogger('seria.load')

    try:
        with open(filepath, 'r', encoding='cp1251') as file:
            lines = file.readlines()
    except IOError:
        logger.error(f'Could not open file: {filepath}')
        return None

    parent_nodes = list()
    header_line = None
    node = None

    for index, line in enumerate(lines):
        line = line.strip()

        if line == '{':
            continue
        elif line == '}':
            # the last '}' will give the last node which is the root node and return it at the end
            node = parent_nodes.pop()
        else:
            # the line before the curly brace is belong the next node
            # e.g. 'm_escadras=327' is belong to node 'Escadra'
            next_index = index + 1
            if next_index < len(lines):
                next_line = lines[next_index].strip()
                if next_line == '{':
                    header_line = line
                    continue

            name, value = _match_attribute(line)

            if name == 'm_classname':
                logger.debug(f'new node: {value}')

                node = SeriaNode(header_line, value)

                if len(parent_nodes) > 0:
                    parent_nodes[-1]._add_child(node)

                parent_nodes.append(node)
            elif name is None:
                node = parent_nodes[-1]

                if node.data_group[0].get('m_classname') == 'Mesh':
                    node._add_attribute('_mesh', line)
            else:
                logger.debug(f'new attribute: {name} = {value}')

                parent_nodes[-1]._add_attribute(name, value)

    return node
