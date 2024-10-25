# HighFleet-SeriaView

[中文](README.zh-cn.md)

A parser that aims to visualize the structure of a seria file for the game HighFleet. It also aims to provide a desktop program that allows easy edit of seria attributes and add nodes into the file.

## Project composition

The project consists of three parts: **Seria Python module**, **Command-line tool** and **Desktop program** (SeriaView).

### Seria Python module

The seria module is the core of this project. It contains a custom data structure that can be used to represent the tree-like structure of a seria file. It also maintains the order of the attribute and provides APIs to read/update attributes and nodes in a file. Once the modification is done. User can easily dump the file back into seria format.  
Below is an example use of the seria module:

```python
import seria
profile = seria.load('profile.seria')
profile.set_attribute('m_scores', '100000') # set player's initial money
profile.set_attribute('m_cash', '100000')   # set player's in-game money
seria.dump(profile, 'profile.seria')        # save changes to the original file
```

### Command-line tool

The command-line tool designed to help analyse the compisition of a seria file by quickly listing attribute names, values and print out tree structure.  
Example usage: `python seria_cli.py -attributes profile.seria`

## Documentation table of content

Seria file tutorial:

- [id dependency of nodes](docs/id%20dependency%20of%20nodes.md)
- [Introduction to Seria profile](docs/Introduction%20to%20Seria%20profile%20structure.md)
- [Seria Lab: add a new ship](docs/Seria%20Lab%20-%20add%20a%20new%20ship.ipynb)
- [Seria Lab: add a new ship (part 2)](docs/Seria%20Lab%20-%20add%20a%20new%20ship%20part2.ipynb)

Seria module tutorial:

- [Introduction to Seria Python module](docs/Introduction%20to%20seria%20Python%20module.md)
- [API Documentation](https://html-preview.github.io/?url=https://github.com/DKAMX/HighFleet-SeriaView/blob/main/docs/seria.html)
