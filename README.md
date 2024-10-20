# HighFleet-SeriaView

[中文](README.zh-cn.md)

A parser that aims to visualize the structure of a seria file for the game HighFleet. It also aims to provide a GUI-based program that allows easy edit of seria attributes and add nodes into the file.

- [Guides](/docs/)  
- API Documentation: [seria](https://html-preview.github.io/?url=https://github.com/DKAMX/HighFleet-SeriaView/blob/main/docs/seria.html)

## Project composition

The project consists of three parts: a `seria` module, a command-line tool (`seria_cli`), and a GUI program.  

### seria module

The `seria` module is the core of this project. It contains a custom data structure that can be used to represent the tree-like structure of a seria file. It also maintains the order of the attribute and provides APIs to read/update attributes and nodes in a file. Once the modification is done. User can easily dump the file back into `seria` format.  
Below is an example use of the `seria` module

```python
import seria
profile = seria.load('profile.seria')
profile.set_attribute('m_scores', '100000') # set player's initial money
profile.set_attribute('m_cash', '100000') # set player's in-game money
seria.dump(profile, 'profile.seria') # save changes to the original file
```

### CLI

The CLI tool designed to help analyse the compisition of a seria file by quickly listing attribute names, values and print out tree structure.  
`python seria_cli.py -attributes profile.seria`
