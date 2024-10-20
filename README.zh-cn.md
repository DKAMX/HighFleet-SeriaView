# HighFleet-SeriaView

[English](README.md)

为高空舰队特有的`seria`格式提供可视化结构的解析器，同时也提供图形界面程序方便查看和编辑（例如存档修改器）。

- [指南](/docs/)  
- API 文档: [seria](https://html-preview.github.io/?url=https://github.com/DKAMX/HighFleet-SeriaView/blob/main/docs/seria.html)

## 项目组成

本项目主要由三个部分组成：`seria` Python 模块，命令行工具（`seria_cli`）和图形界面程序（SeriaView）。

### seria 模块

`seria`模块是这个项目的核心。它包括一个自定义的数据结构用来表示seria文件的树状结构。它同时还维持了文件原有属性和节点的顺序，并提供接口对属性和节点进行读写操作。操作完成后，用户可以很轻松的将对象重新导出为`seria`格式的文件。  
以下是使用`seria`模块的简单例子。

```python
import seria
profile = seria.load('profile.seria')
profile.set_attribute('m_scores', '100000') # set player's initial money
profile.set_attribute('m_cash', '100000') # set player's in-game money
seria.dump(profile, 'profile.seria') # save changes to the original file
```

### 命令行

命令行工具被设计成用来帮助分析seria文件的构成，例如列出所有的属性名称，特点属性的出现的值以及打印树结构。  
用例：`python seria_cli.py -attributes profile.seria`
