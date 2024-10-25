# Introduction to Seria Python module

Seria module is a python module that contains functions and custom data types that can represent seria file as a tree structure. A seria file can be seen as a node that contains numerous attributes and sub nodes. This is similar to JSON which contains key-value pairs and the value type can also be JSON (nested JSON object).  

Seria file is order-sensitive. Certain attributes must present in correct order. For example, `m_tele_total` must appear before `m_tele_capacity`, these two attributes are crucial to functional of a ship node. And incorrect order can cause attribute to be lost, thus lead to game crash.  
Recent Python distribution have made OrderedDict as default. When iterate through the dictionary. Items will present in the order as they were inserted in the first place. However, dictionary does not support insertion like an actual list. As a result, we need to have a special data type that allows easy key-value retrival as well as insertion based on index.

## How to use seria module

Simply have a copy of [seria.py](../seria.py), and `import seria` in your Python script. The design of API refers to the standard JSON library in Python. It's fairly simple: just `load` file to acquire a `SeriaNode` object for modification, and `dump` the object to output as a seria file.

## Internal structure of SeriaNode

SeriaNode manage attributes and child nodes of a node as a list in internal. We have the concept of data list which perceive attribute and node all as a chunk of data. Doing so we can easily manage it's order without looking into the detail of the data. But sure, we will have different data type for the two. Custom `alist` type for attributes and `SeriaNode` for the child node. A typical seria profile looks like this in the memeory:

```plaintext
alist       <- attributes placed before the first child node
SeriaNode   <- multiple child nodes (internal structure omitted but similar to this one)
...
SeriaNode
alist       <- attributes placed after the last child node
```

When query on attribute of the current node. It will iterate through this data list but ignore child node and combines all `alist` as one `dict` object (here we assume that attribute won't appear in two sperate location). On the API surface level, you don't need to worry about which `alist` to look for. Because the node will handle it for you.  

As for node sequence. It will also iterate through. But one thing worth to notice is when using method such as `get_node(self, index: int)`. The `index` refers to only the order of the child node. For example, we have 3 child nodes in current node. Ignore all `alist` object. Child nodes should have such index sequence: 0, 1, 2.

## Shallow copy and deep copy  

By default, seria will gives you reference to the original object. For example:

```python
import seria
profile = seria.load('profile.seria')
ammo = profile.get_node_by_class('Item')    # get the first Item node (Ammo item) in the profile node
ammo.set_attribute('m_count', '100')        # set ammo amount to 100
```

In this example, modification on the `ammo` will reflect on the original `profile` object. And you don't need to put `ammo` back to `profile`. However, if you do want a deep copy of the object. Use `copy` module from the Python standard library:

```python
from copy import deepcopy
ammo2 = deepcopy(ammo)
```

Here, if we modify `ammo2`. `ammo` and `profile` object will not change accordingly.
