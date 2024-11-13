# 高空舰队 SeriaView

[English](README.md)

为高空舰队特有的`seria`格式提供可视化结构的解析器，同时也提供图形界面程序方便查看和编辑（例如存档修改器）。

## 项目组成

项目主要由三个部分组成：**Seria Python模块**，**命令行工具**以及**桌面端程序** （SeriaView）。  

[桌面端程序的说明](README.txt)

### Seria Python 模块

seria模块是这个项目的核心。它包括一个自定义的数据结构用来表示seria文件的树状结构。它同时还维持了文件原有属性和节点的顺序，并提供接口对属性和节点进行读写操作。操作完成后，用户可以很轻松的将对象重新导出为seria格式的文件。  
以下是使用seria模块的简单例子：

```python
import seria
profile = seria.load('profile.seria')
profile.set_attribute('m_scores', '100000') # 设置玩家的初始金钱
profile.set_attribute('m_cash', '100000')   # 设置当前战役内的金钱
seria.dump(profile, 'profile.seria')        # 保存更改到原始文件
```

### 命令行工具

命令行工具被设计成用来帮助分析seria文件的构成，例如列出所有的属性名称，特点属性的出现的值以及打印树结构。  
用例：`python seria_cli.py -attributes profile.seria`

## 文档目录

Seria 文件教程：

- [id dependency of nodes](docs/id%20dependency%20of%20nodes.md)
- [Seria 存档入门](docs/Introduction%20to%20Seria%20profile%20structure.zh-cn.md)
- [Seria Lab: add a new ship](docs/Seria%20Lab%20-%20add%20a%20new%20ship.ipynb)
- [Seria Lab: add a new ship (part 2)](docs/Seria%20Lab%20-%20add%20a%20new%20ship%20part2.ipynb)
- [Seria Lab: add a new part to inventory](docs/SeriaLab%20-%20add%20part%20to%20inventory.ipynb)

Seria 模块教程：

- [Introduction to Seria Python module](docs/Introduction%20to%20seria%20Python%20module.md)
- [API 文档](https://html-preview.github.io/?url=https://github.com/DKAMX/HighFleet-SeriaView/blob/main/docs/seria.html)
