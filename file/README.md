# 文件系统管理——详细说明文档

## 1. 项目概述

### 1.1 项目背景
本项目是同济大学软件学院操作系统课程的文件系统管理项目。通过在内存中模拟磁盘空间，实现了一个基于FAT表和多级目录结构的简单文件系统，提供了完整的文件创建、修改、删除等操作功能。

### 1.2 系统架构
该文件系统包含以下主要组件：
- 磁盘空间模拟模块
- FAT表管理模块
- 目录结构管理模块
- 文件操作模块
- 用户界面模块

## 2. 系统功能

### 2.1 用户界面
系统提供了直观的图形用户界面，包括：
- 左侧多级目录树形展示
- 上部当前路径导航栏
- 右侧文件和文件夹图标化展![image-20250621190849076](C:\Users\dell\AppData\Roaming\Typora\typora-user-images\image-20250621190849076.png)

#### 2.1.1 界面实现代码
界面基于PyQt5实现，主界面在`main.py`中的`MainForm`类中定义：

```python
class MainForm(QMainWindow):
    def __init__(self):
        super().__init__()
        # 加载文件数据
        self.read_file()
        # 设置根目录
        self.cur_node = self.catalog[0]
        self.root_node = self.cur_node
        self.base_url = ['root']
        # 设置应用样式
        self.setStyleSheet(APP_STYLE)
        # 窗口设置
        self.resize(1200, 800)
        self.setWindowTitle('File Management System')
        self.setWindowIcon(QIcon('img/folder.ico'))
```

界面布局采用网格布局和分割器实现左右面板：

```python
# 创建分割器实现可调整大小的面板
splitter = QSplitter(Qt.Horizontal)
grid.addWidget(splitter, 1, 0)

# 创建文件树视图
self.setup_file_tree()
splitter.addWidget(self.tree)

# 创建文件列表视图
self.setup_file_list_view()
splitter.addWidget(self.list_view)

# 设置默认分割器大小（左面板30%，右面板70%）
splitter.setSizes([int(self.width() * 0.3), int(self.width() * 0.7)])
```

### 2.2 文件管理功能

#### 2.2.1 文件和文件夹操作
- 创建新文件/文件夹

- 删除文件/文件夹

- 重命名文件/文件夹

- 查看文件/文件夹属性

  ![image-20250621191021876](C:\Users\dell\AppData\Roaming\Typora\typora-user-images\image-20250621191021876.png)

  ![image-20250621191040875](C:\Users\dell\AppData\Roaming\Typora\typora-user-images\image-20250621191040875.png)

  ![image-20250621190954710](C:\Users\dell\AppData\Roaming\Typora\typora-user-images\image-20250621190954710.png)

##### 创建文件实现代码
```python
def create_file(self):
    """创建新文件"""
    # 获取当前时间
    current_time = time.localtime()
    
    # 生成默认文件名
    base_name = "New File"
    new_name = base_name
    count = 1
    
    # 检查是否有重名文件
    while any(node.name == new_name for node in self.cur_node.children):
        new_name = f"{base_name} ({count})"
        count += 1
    
    # 创建新的目录节点（文件）
    new_node = CatalogNode(new_name, True, self.fat, self.disk, current_time, self.cur_node)
    self.cur_node.children.append(new_node)
    
    # 更新界面显示
    self.update_print()
    self.update_tree()
    
    # 编辑新创建的文件名
    self.list_view.edit_last()
```

##### 删除文件实现代码
```python
def delete_file(self):
    """删除文件或文件夹"""
    # 获取选中的项目
    items = self.list_view.selectedItems()
    if not items:
        return
        
    # 确认删除
    reply = QMessageBox.question(
        self, '确认', f'确定要删除选中的 {len(items)} 个项目吗？',
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    )
    
    if reply == QMessageBox.Yes:
        # 获取要删除的节点索引
        indexes = [self.list_view.row(item) for item in items]
        indexes.sort(reverse=True)  # 从后向前删除
        
        for index in indexes:
            # 删除文件占用的磁盘空间
            if self.cur_node.children[index].is_file:
                self.cur_node.children[index].data.delete(self.fat, self.disk)
            else:
                # 递归删除文件夹内容
                self.delete_file_recursive(self.cur_node.children[index])
                
            # 从目录结构中移除
            del self.cur_node.children[index]
            
        # 更新界面
        self.update_print()
        self.update_tree()
```

#### 2.2.2 文件系统操作
- 格式化磁盘

- 查看系统信息

- 查看磁盘使用情况

  ![image-20250621191114506](C:\Users\dell\AppData\Roaming\Typora\typora-user-images\image-20250621191114506.png)

##### 格式化磁盘实现代码
```python
def format(self):
    """格式化磁盘"""
    # 确认操作
    reply = QMessageBox.question(
        self, '确认格式化', '确定要格式化磁盘吗？所有数据将丢失！',
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    )
    
    if reply == QMessageBox.Yes:
        # 重新初始化FAT表和磁盘
        self.fat = FAT()
        self.disk = [Block(i) for i in range(BLOCK_NUM)]
        
        # 重新创建根目录
        current_time = time.localtime()
        self.catalog = [CatalogNode('root', False, self.fat, self.disk, current_time)]
        self.cur_node = self.catalog[0]
        self.root_node = self.cur_node
        
        # 重置导航历史
        self.base_url = ['root']
        self.back_list = []
        self.forward_list = []
        
        # 更新界面
        self.update_print()
        self.update_tree()
        self.update_loc()
        
        QMessageBox.information(self, '格式化完成', '磁盘已成功格式化')
```

### 2.3 导航功能
- 前进/后退操作
- 直接通过路径导航
- 通过目录树跳转

#### 导航功能实现代码
```python
def back_event(self):
    """后退操作"""
    if not self.back_list:
        return
        
    # 保存当前位置到前进列表
    self.forward_list.append({
        'node': self.cur_node,
        'url': self.base_url.copy()
    })
    
    # 从后退列表获取上一个位置
    last = self.back_list.pop()
    self.cur_node = last['node']
    self.base_url = last['url']
    
    # 更新界面
    self.update_print()
    self.update_loc()

def forward_event(self):
    """前进操作"""
    if not self.forward_list:
        return
        
    # 保存当前位置到后退列表
    self.back_list.append({
        'node': self.cur_node,
        'url': self.base_url.copy()
    })
    
    # 从前进列表获取下一个位置
    next_pos = self.forward_list.pop()
    self.cur_node = next_pos['node']
    self.base_url = next_pos['url']
    
    # 更新界面
    self.update_print()
    self.update_loc()
```

## 3. 技术实现

### 3.1 存储管理
本系统使用FAT（文件分配表）来管理文件的存储空间。FAT表中每个表项记录了文件下一个块的位置，形成一个链式结构，通过这种方式可以有效地管理文件的分配和回收。

#### FAT表实现代码
```python
class FAT:
    """文件分配表实现"""
    def __init__(self):
        # 初始化FAT表，-2表示空闲块
        self.fat: List[int] = [-2] * BLOCK_NUM

    def find_blank(self) -> int:
        """查找第一个可用块"""
        for i in range(BLOCK_NUM):
            if self.fat[i] == -2:
                return i
        return -1
    
    def write(self, data: str, disk: List[Block]) -> int:
        """
        将数据写入磁盘，根据需要分配块
        返回起始块索引
        """
        start = -1
        cur = -1

        while data:
            # 查找空闲块
            new_loc = self.find_blank()
            if new_loc == -1:
                raise Exception("磁盘空间不足！")
            
            # 更新FAT链表
            if cur != -1:
                self.fat[cur] = new_loc
            else:
                start = new_loc
                
            cur = new_loc
            # 将数据写入块，返回剩余数据
            data = disk[cur].write(data)
            # -1表示文件结束
            self.fat[cur] = -1

        return start
```

### 3.2 目录结构
系统采用多级目录结构，每个目录项包含：
- 文件名
- 物理地址（FAT表中的起始位置）
- 文件大小
- 创建时间
- 修改时间
- 文件属性

#### 目录结构实现代码
```python
class CatalogNode:
    """目录树节点，用于多级目录结构"""
    def __init__(self, name: str, is_file: bool, fat: FAT, disk: List[Block], 
                 create_time: time.struct_time, parent: Optional['CatalogNode'] = None, 
                 data: str = ""):
        self.name = name
        self.is_file = is_file
        self.parent = parent
        self.create_time = create_time
        self.update_time = self.create_time
        
        # 如果是目录，创建子节点列表；如果是文件，创建FCB
        if not self.is_file:
            self.children: List['CatalogNode'] = []
        else:
            self.data = FCB(name, create_time, data, fat, disk)
```

### 3.3 文件操作实现
文件的读写操作通过定位FAT表中的起始位置，并根据FAT表的链接关系找到所有的数据块来实现。系统支持文件的随机读写，可以高效地处理大文件。

#### 文件控制块实现代码
```python
class FCB:
    """文件控制块，用于管理文件元数据"""
    def __init__(self, name: str, create_time: time.struct_time, data: str, fat: FAT, disk: List[Block]):
        self.name = name
        self.create_time = create_time
        self.update_time = self.create_time
        # 将数据写入磁盘，记录起始块位置
        self.start = fat.write(data, disk) if data else -1
    
    def update(self, new_data: str, fat: FAT, disk: List[Block]) -> None:
        """更新文件内容"""
        self.start = fat.update(self.start, new_data, disk)
        self.update_time = time.localtime()
    
    def delete(self, fat: FAT, disk: List[Block]) -> None:
        """从磁盘删除文件"""
        fat.delete(self.start, disk)
    
    def read(self, fat: FAT, disk: List[Block]) -> str:
        """读取文件内容"""
        if self.start == -1:
            return ""
        return fat.read(self.start, disk)
```

### 3.4 文件编辑功能
系统提供了基本的文件编辑功能，用户可以创建、打开、编辑和保存文本文件，支持基本的文本操作。

![image-20250621191149703](C:\Users\dell\AppData\Roaming\Typora\typora-user-images\image-20250621191149703.png)

#### 文件编辑器实现代码
```python
class EditForm(QWidget):
    """文件编辑对话框"""
    # 信号，用于通知父窗口内容变更
    _signal = pyqtSignal(str)

    def __init__(self, name: str, data: str):
        super().__init__()
        
        # 窗口设置
        self.resize(1200, 800)
        self.setWindowTitle(name)
        self.name = name
        self.setWindowIcon(QIcon('img/file.png'))
        self.resize(412, 412)
        
        # 文本编辑器设置
        self.text_edit = QTextEdit(self)
        self.text_edit.setText(data)
        self.text_edit.setPlaceholderText("在此输入文件内容")
        self.text_edit.textChanged.connect(self.change_message)
        self.initial_data = data

        # 布局设置
        self.h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.text_edit)
        self.v_layout.addLayout(self.h_layout)
        self.setLayout(self.v_layout)

        # 设置为模态对话框
        self.setWindowModality(Qt.ApplicationModal)
```
### 3.5 持久化存储功能

![image-20250621191344225](C:\Users\dell\AppData\Roaming\Typora\typora-user-images\image-20250621191344225.png)

系统通过pickle模块实现文件系统状态的持久化存储：

```python
def save_file(self):
    """保存文件系统状态"""
    with open('disk', 'wb') as f:
        pickle.dump(self.disk, f)
    with open('fat', 'wb') as f:
        pickle.dump(self.fat, f)
    with open('catalog', 'wb') as f:
        pickle.dump(self.catalog, f)

def read_file(self):
    """读取文件系统状态"""
    try:
        with open('disk', 'rb') as f:
            self.disk = pickle.load(f)
        with open('fat', 'rb') as f:
            self.fat = pickle.load(f)
        with open('catalog', 'rb') as f:
            self.catalog = pickle.load(f)
    except:
        # 如果读取失败，初始化新的文件系统
        self.initial()
```
## 4. 使用说明

### 4.1 系统启动
系统启动后，会自动加载文件系统。如果是首次使用，系统会自动进行初始化和格式化操作。

#### 系统初始化代码
```python
def initial(self):
    """初始化文件系统"""
    # 创建FAT表
    self.fat = FAT()
    # 创建磁盘块
    self.disk = [Block(i) for i in range(BLOCK_NUM)]
    
    # 创建根目录
    current_time = time.localtime()
    self.catalog = [CatalogNode('root', False, self.fat, self.disk, current_time)]
    
    # 创建示例文件和文件夹
    readme = CatalogNode('README.txt', True, self.fat, self.disk, current_time, self.catalog[0], 
                        "这是一个简单的文件系统示例。\n您可以创建、编辑、删除文件和文件夹。")
    docs = CatalogNode('Documents', False, self.fat, self.disk, current_time, self.catalog[0])
    
    # 添加到根目录
    self.catalog[0].children.append(readme)
    self.catalog[0].children.append(docs)
    
    # 保存文件系统状态
    self.save_file()
```

### 4.2 文件操作
- **创建文件/文件夹**：右键点击空白区域，选择"新建文件"或"新建文件夹"
- **打开文件**：双击文件图标或右键选择"打开"
- **删除文件/文件夹**：选中后按Delete键或右键选择"删除"
- **重命名**：选中后按F2键或右键选择"重命名"
- **查看属性**：右键选择"属性"

#### 右键菜单实现代码
```python
def show_menu(self, point):
    """显示右键菜单"""
    # 创建菜单
    menu = QMenu(self.list_view)
    
    # 获取选中项目
    items = self.list_view.selectedItems()
    
    if items:
        # 如果有选中项目，添加相关操作
        if len(items) == 1:
            item = items[0]
            index = self.list_view.row(item)
            node = self.cur_node.children[index]
            
            # 根据是文件还是文件夹添加不同操作
            if node.is_file:
                menu.addAction(QIcon("img/file.png"), "打开", lambda: self.open_file(self.list_view.indexFromItem(item)))
            else:
                menu.addAction(QIcon("img/folder.png"), "打开", lambda: self.open_file(self.list_view.indexFromItem(item)))
                
            menu.addSeparator()
            
        # 通用操作
        menu.addAction(QIcon(), "删除", self.delete_file)
        menu.addAction(QIcon(), "重命名", self.rename)
        
        if len(items) == 1:
            menu.addAction(QIcon("img/attribute.png"), "属性", self.view_attribute)
    else:
        # 如果没有选中项目，显示创建操作
        menu.addAction(QIcon(), "新建文件", self.create_file)
        menu.addAction(QIcon(), "新建文件夹", self.create_folder)
    
    # 显示菜单
    menu.exec_(self.list_view.mapToGlobal(point))
```

### 4.3 导航操作
- **进入文件夹**：双击文件夹图标或在左侧目录树中点击
- **返回上级目录**：点击导航栏中的上级目录或使用后退按钮
- **前进/后退**：使用工具栏中的前进/后退按钮

#### 目录树点击实现代码
```python
def click_tree_item(self, item, column):
    """处理目录树点击事件"""
    # 保存当前位置到后退列表
    self.back_list.append({
        'node': self.cur_node,
        'url': self.base_url.copy()
    })
    
    # 清空前进列表
    self.forward_list = []
    
    # 获取点击的路径
    path = []
    temp = item
    while temp:
        path.append(temp.text(0))
        temp = temp.parent()
    
    path.reverse()
    
    # 从根目录开始查找目标节点
    target_node = self.root_node
    for i in range(1, len(path)):
        for child in target_node.children:
            if not child.is_file and child.name == path[i]:
                target_node = child
                break
    
    # 更新当前节点和路径
    self.cur_node = target_node
    self.base_url = path
    
    # 更新界面
    self.update_print()
    self.update_loc()
```

## 5. 系统特色

### 5.1 直观的图形界面
系统采用现代化的图形界面设计，操作简单直观，用户可以像使用真实文件系统一样操作。

### 5.2 完整的文件系统功能
尽管是模拟实现，但系统提供了完整的文件系统功能，包括文件的创建、删除、重命名、属性查看等，以及目录的多级管理。

### 5.3 高效的存储管理
通过FAT表实现了高效的文件存储空间管理，支持文件的动态分配和回收。

#### 磁盘块实现代码
```python
class Block:
    """磁盘物理块"""
    def __init__(self, block_index: int, data: str = ""):
        self.block_index = block_index
        self.data = data
    
    def write(self, new_data: str) -> str:
        """写入数据到块并返回无法容纳的剩余数据"""
        self.data = new_data[:BLOCK_SIZE]
        return new_data[BLOCK_SIZE:]
    
    def read(self) -> str:
        """从块读取数据"""
        return self.data

    def is_full(self) -> bool:
        """检查块是否已满"""
        return len(self.data) == BLOCK_SIZE

    def append(self, new_data: str) -> str:
        """向块追加新数据并返回无法容纳的数据"""
        remain_space = BLOCK_SIZE - len(self.data)
        if remain_space >= len(new_data):
            self.data += new_data
            return ""
        else:
            self.data += new_data[:remain_space]
            return new_data[remain_space:]
```

## 6. 项目环境与运行

### 6.1 开发环境
- Python 3.8
- PyQt5 (用于图形界面)

### 6.2 运行方法
1. **代码运行**：通过Python运行代码  
```
python main.py
```

### 6.3 系统要求
- 操作系统：Windows 7/8/10/11, macOS, Linux
- 内存：至少512MB
- 磁盘空间：至少100MB
