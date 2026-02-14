"""
Main application for the file management system
"""
import sys
import os
import pickle
import time
from typing import List, Optional, Dict, Any, Tuple

from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QDesktopWidget, QGridLayout, 
    QAction, QLineEdit, QFormLayout, QTreeWidget, QTreeWidgetItem, 
    QListView, QAbstractItemView, QMessageBox, QMenu, QShortcut,
    QListWidgetItem, QSplitter
)
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel, QKeySequence, QPalette, QColor, QFont
from PyQt5.QtCore import QSize, Qt, QModelIndex, QTimer

from File import CatalogNode, FAT, Block, BLOCK_NUM
from MyWidget import MyListWidget
from fileEdit import EditForm, AttributeForm


# 定义应用程序样式
APP_STYLE = """
QMainWindow {
    background-color: #f5f5f5;
}

QMenuBar {
    background-color: #2c3e50;
    color: white;
    padding: 4px;
    font-weight: bold;
}

QMenuBar::item {
    background-color: #2c3e50;
    color: white;
    padding: 6px 12px;
    margin: 2px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #34495e;
}

QToolBar {
    background-color: #ecf0f1;
    border-bottom: 1px solid #bdc3c7;
    padding: 5px;
    spacing: 8px;
}

QLineEdit {
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 8px;
    background-color: white;
    selection-background-color: #3498db;
}

QTreeWidget {
    background-color: #ecf0f1;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 4px;
}

QTreeWidget::item {
    padding: 6px;
    margin: 2px 0;
}

QTreeWidget::item:selected {
    background-color: #3498db;
    color: white;
    border-radius: 4px;
}

QListView {
    background-color: white;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 10px;
}

QListView::item:selected {
    background-color: #3498db;
    color: white;
    border-radius: 4px;
}

QStatusBar {
    background-color: #2c3e50;
    color: white;
    padding: 6px;
}

QMenu {
    background-color: white;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 5px;
}

QMenu::item {
    padding: 6px 30px 6px 30px;
    border-radius: 3px;
    margin: 2px;
}

QMenu::item:selected {
    background-color: #3498db;
    color: white;
}

QMessageBox {
    background-color: white;
}

QPushButton {
    background-color: #3498db;
    color: white;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #1f6aa5;
}
"""


class MainForm(QMainWindow):
    """
    Main window for the file management system
    """
    def __init__(self):
        super().__init__()

        # Load file data
        self.read_file()

        # Set up root directory
        self.cur_node = self.catalog[0]
        self.root_node = self.cur_node
        self.base_url = ['root']

        # Set application style
        self.setStyleSheet(APP_STYLE)
        
        # Window setup
        self.resize(1200, 800)
        self.setWindowTitle('File Management System')
        self.setWindowIcon(QIcon('img/folder.ico'))

        # Center window on screen
        qr = self.frameGeometry()
        center_place = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(center_place)
        self.move(qr.topLeft())

        # Set up layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        main_widget.setLayout(grid)
        
        # Create menu bar
        self.setup_menu_bar()
        
        # Create toolbar
        self.setup_toolbar()

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        grid.addWidget(splitter, 1, 0)

        # Create file tree view
        self.setup_file_tree()
        splitter.addWidget(self.tree)

        # Create file list view
        self.setup_file_list_view()
        splitter.addWidget(self.list_view)
        
        # Set default splitter sizes (30% left panel, 70% right panel)
        splitter.setSizes([int(self.width() * 0.3), int(self.width() * 0.7)])

        # Set up context menu
        self.list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_view.customContextMenuRequested.connect(self.show_menu)

        # Update UI
        self.update_print()
        self.last_loc = -1

        # Set up keyboard shortcuts
        QShortcut(QKeySequence(self.tr("Delete")), self, self.delete_file)
    
    def setup_menu_bar(self):
        """
        Set up the application menu bar
        """
        # Exit action
        exit_action = QAction(QIcon('file.png'), 'Exit', self)        
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(QApplication.quit)

        # Menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Add more file actions
        new_file_action = QAction(QIcon('img/file.png'), 'New File', self)
        new_file_action.setShortcut('Ctrl+N')
        new_file_action.triggered.connect(self.create_file)
        file_menu.addAction(new_file_action)
        
        new_folder_action = QAction(QIcon('img/folder.png'), 'New Folder', self)
        new_folder_action.setShortcut('Ctrl+Shift+N')
        new_folder_action.triggered.connect(self.create_folder)
        file_menu.addAction(new_folder_action)
        
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('Edit')
        
        # Add edit actions
        delete_action = QAction('Delete', self)
        delete_action.setShortcut('Delete')
        delete_action.triggered.connect(self.delete_file)
        edit_menu.addAction(delete_action)
        
        rename_action = QAction('Rename', self)
        rename_action.setShortcut('F2')
        rename_action.triggered.connect(self.rename)
        edit_menu.addAction(rename_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        # Add view actions
        large_icons_action = QAction('Large Icons', self)
        large_icons_action.triggered.connect(lambda: self.change_icon_size(172, 200))
        view_menu.addAction(large_icons_action)
        
        medium_icons_action = QAction('Medium Icons', self)
        medium_icons_action.triggered.connect(lambda: self.change_icon_size(72, 100))
        view_menu.addAction(medium_icons_action)
        
        small_icons_action = QAction('Small Icons', self)
        small_icons_action.triggered.connect(lambda: self.change_icon_size(56, 84))
        view_menu.addAction(small_icons_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        # Add format action to tools menu
        format_action = QAction('Format Disk', self)
        format_action.triggered.connect(self.format)
        tools_menu.addAction(format_action)
        
        # Help action
        menubar.addAction('Help', self.introduction)
    
    def change_icon_size(self, icon_size, grid_size):
        """
        Change the size of icons in the list view
        """
        self.list_view.setIconSize(QSize(icon_size, icon_size))
        self.list_view.setGridSize(QSize(grid_size, grid_size))
    
    def setup_toolbar(self):
        """
        Set up the application toolbar
        """
        # Create toolbar
        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(24, 24))
        
        # Back button
        self.back_action = QAction(QIcon('img/back.png'), 'Back', self)
        self.back_action.setShortcut('Alt+Left')
        self.back_action.triggered.connect(self.back_event)
        self.toolbar.addAction(self.back_action)
        self.back_action.setEnabled(False)

        # Forward button
        self.forward_action = QAction(QIcon('img/forward.png'), 'Forward', self)
        self.forward_action.setShortcut('Alt+Right')
        self.forward_action.triggered.connect(self.forward_event)
        self.toolbar.addAction(self.forward_action)
        self.forward_action.setEnabled(False)

        # Home button
        home_action = QAction(QIcon('img/folder.png'), 'Home', self)
        home_action.triggered.connect(self.go_home)
        self.toolbar.addAction(home_action)

        self.toolbar.addSeparator()

        # Add file and folder buttons to toolbar
        create_file_action = QAction(QIcon('img/file.png'), 'New File', self)
        create_file_action.triggered.connect(self.create_file)
        self.toolbar.addAction(create_file_action)
        
        create_folder_action = QAction(QIcon('img/folder.png'), 'New Folder', self)
        create_folder_action.triggered.connect(self.create_folder)
        self.toolbar.addAction(create_folder_action)
        
        self.toolbar.addSeparator()

        # Current location
        self.cur_location = QLineEdit()
        self.cur_location.setText('> root')
        self.cur_location.setReadOnly(True)
        self.cur_location.addAction(QIcon('img/folder.png'), QLineEdit.LeadingPosition)
        self.cur_location.setMinimumHeight(40)
        self.cur_location.setFont(QFont("Arial", 10))
        
        # Add location to toolbar
        ptr_layout = QFormLayout()
        ptr_layout.addRow(self.cur_location)
        ptr_widget = QWidget()
        ptr_widget.setLayout(ptr_layout) 
        ptr_widget.adjustSize()
        self.toolbar.addWidget(ptr_widget)
    
    def go_home(self):
        """
        Navigate back to root directory
        """
        # If already at root, do nothing
        if self.cur_node == self.root_node:
            return
        
        # Return to root directory
        while self.back_event():
            pass
    
    def setup_file_tree(self):
        """
        Set up the file tree view
        """
        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabels(['Folders'])
        self.tree.setMinimumWidth(250)  # Set minimum width
        self.tree.setFont(QFont("Arial", 10))
        
        # Build tree
        self.build_tree()
        
        # Set selection
        self.tree.setCurrentItem(self.root_item)
        self.tree_item = [self.root_item]
        
        # Connect click event
        self.tree.itemClicked['QTreeWidgetItem*', 'int'].connect(self.click_tree_item)
    
    def setup_file_list_view(self):
        """
        Set up the file list view
        """
        self.list_view = MyListWidget(self.cur_node, parents=self)
        self.list_view.setMinimumWidth(800)
        self.list_view.setViewMode(QListView.IconMode)
        self.list_view.setIconSize(QSize(72, 72))
        self.list_view.setGridSize(QSize(100, 100))
        self.list_view.setResizeMode(QListView.Adjust)
        self.list_view.setMovement(QListView.Static)
        self.list_view.doubleClicked.connect(self.open_file)
        self.list_view.setFont(QFont("Arial", 10))
        self.list_view.setSpacing(10)  # Add spacing between icons
        self.list_view.setUniformItemSizes(True)  # Improve layout performance

        # Animation effects for selection
        self.list_view.setSelectionRectVisible(True)

        # Load current directory files
        self.load_cur_file()

    def introduction(self):
        """
        Display help information about the application
        """
        QMessageBox.about(self, 'Help', 
        'File Management System\n\n'+
        'This project simulates a file management system using FAT tables and multi-level directory structures\n'+
        '-----------------------------------------\n'+
        'Open file: Right-click or double-click to open a file\n'+
        'Delete file: Right-click or press Delete key to remove a file\n'+
        'Left sidebar: View directory structure and click to navigate\n'+
        'Properties: Right-click a file to view properties, or view current folder properties\n'+
        'Create new: Right-click to create new files or folders\n'+
        'Rename: Right-click to rename files or folders\n'+
        'Format: Clear all content\n'+
        'Navigation bar: View current path\n'+
        'Back/Forward: Return to parent directory or navigate to previously visited locations\n'+
        '-----------------------------------------\n')

    def click_tree_item(self, item, column):
        ways = [item]
        #查看所在层数
        level = 0
        temp = item
        
        while temp.parent() != None:
            temp = temp.parent()
            ways.append(temp)
            level += 1
 
        ways.reverse()
        #回退到根节点
        while self.back_event():
            pass
        self.base_url = self.base_url[:1]
        self.tree_item = self.tree_item[:1]

        #一步一步前进
        for i in ways:
            if i == self.root_item:
                continue
            #前往该路径
            #从curNode中查询item
            new_node = None
            for j in self.cur_node.children:
                if j.name == i.text(0):
                    new_node = j
                    break
            #前往路径j
            if new_node.is_file:
                #文件的话，break即可
                break
            else:
                self.cur_node = new_node
                self.update_loc()
                self.base_url.append(new_node.name)

                #更新路径
                for j in range(self.tree_item[-1].childCount()):
                    if self.tree_item[-1].child(j).text(0) == new_node.name:
                        selected_item = self.tree_item[-1].child(j)
                self.tree_item.append(selected_item)
                self.tree.setCurrentItem(selected_item)
        
        #更新下标
        self.update_print()
        
        if self.cur_node != self.root_node:
            self.back_action.setEnabled(True)
        
        self.forward_action.setEnabled(False)
        self.last_loc = -1

    def update_loc(self):
        self.load_cur_file()
        self.list_view.cur_node = self.cur_node

    #打开文件
    def open_file(self, modelindex: QModelIndex) -> None:
        #获取点击item
        self.list_view.close_edit()

        try:
            item = self.list_view.item(modelindex.row())
        except:
            #报错，则说明是右键打开方式
            if len(self.list_view.selectedItems()) == 0:
                return
            item = self.list_view.selectedItems()[-1]

        #如果可以前进
        if self.last_loc != -1 and self.next_step:
            item = self.list_view.item(self.last_loc)
            self.last_loc = -1
            self.forward_action.setEnabled(False)
        self.next_step = False

        new_node = None
        for i in self.cur_node.children:
            if i.name == item.text():
                new_node = i
                break

        if new_node.is_file:
            data = new_node.data.read(self.fat, self.disk)
            self.child = EditForm(new_node.name, data)
            self.child._signal.connect(self.getData)
            self.child.show()
            self.write_file = new_node
        else:
            #进下一级目录前，如果处于编辑状态，一定要取消编辑
            self.list_view.close_edit()

            self.cur_node = new_node
            self.update_loc()
            self.base_url.append(new_node.name)

            #更新路径
            for i in range(self.tree_item[-1].childCount()):
                if self.tree_item[-1].child(i).text(0) == new_node.name:
                    selected_item = self.tree_item[-1].child(i)
            self.tree_item.append(selected_item)
            self.tree.setCurrentItem(selected_item)
            self.back_action.setEnabled(True)

            self.update_print()

    def update_print(self):
        """
        Update status bar and location display
        """
        # Create a colorful status bar message
        status_message = f"{len(self.cur_node.children)} items | File Management System"
        self.statusBar().showMessage(status_message)
        
        # Update path display with modern formatting
        s = '> root'
        for i, item in enumerate(self.base_url):
            if i == 0:
                continue
            s += " > " + item
                
        self.cur_location.setText(s)

    def rename(self):
        """
        Rename the selected file or folder
        """
        if len(self.list_view.selectedItems()) == 0:
            return
        
        # 关闭之前的编辑状态
        self.list_view.close_edit()
        
        # Get the last selected item index
        index = self.list_view.selectedIndexes()[-1].row()
        
        # Start editing the item
        self.list_view.edit_selected(index)
        
        # Make sure item gets focus
        self.list_view.setFocus()

    def delete_file(self):
        """
        Delete file or folder
        """
        if len(self.list_view.selectedItems()) == 0:
            return

        item = self.list_view.selectedItems()[-1]
        index = self.list_view.selectedIndexes()[-1].row()

        # Confirmation dialog
        reply = QMessageBox()
        reply.setWindowTitle('Confirm')
        
        # Different message based on file type
        if self.cur_node.children[index].is_file:
            reply.setText(f'Are you sure you want to delete the file "{item.text()}"?')
        else:
            reply.setText(f'Are you sure you want to delete the folder "{item.text()}" and all its contents?')
            
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        buttonY = reply.button(QMessageBox.Yes)
        buttonY.setText('Yes')
        buttonN = reply.button(QMessageBox.No)
        buttonN.setText('No')

        reply.exec_()

        if reply.clickedButton() == buttonN:
            return
        
        # Delete file
        self.list_view.takeItem(index)
        del item
        # Delete from FAT table
        self.delete_file_recursive(self.cur_node.children[index])
        self.cur_node.children.remove(self.cur_node.children[index])
        # Update catalog
        self.catalog = self.update_catalog(self.root_node)

        # Update UI
        self.update_tree()

    def delete_file_recursive(self, node):
        if node.is_file:
            node.data.delete(self.fat, self.disk)
        else:
            for i in node.children:
                self.delete_file_recursive(i)
   

    def update_catalog(self, node):
        if node.is_file:
            return [node]
        else:
            x = [node]
            for i in node.children:
                x += self.update_catalog(i)
            return x

    def create_folder(self):
        """
        Create a new folder in the current directory
        """
        # 关闭之前的编辑状态
        self.list_view.close_edit()
        
        # Check for duplicate names and generate unique name
        folder_name = "New Folder"
        count = 1
        while any(node.name == folder_name for node in self.cur_node.children):
            folder_name = f"New Folder ({count})"
            count += 1
            
        # Create new item
        self.item_1 = QListWidgetItem(QIcon("img/folder.png"), folder_name)
        self.list_view.addItem(self.item_1)

        # Add to directory tree
        new_node = CatalogNode(folder_name, False, self.fat, self.disk, time.localtime(time.time()), self.cur_node)
        self.cur_node.children.append(new_node)
        self.catalog.append(new_node)

        # Update tree
        self.update_tree()
        
        # Set focus and edit
        self.list_view.setCurrentItem(self.item_1)
        self.list_view.setFocus()
        
        # 延迟一下激活编辑，确保UI已更新
        QTimer.singleShot(100, self.list_view.edit_last)

    def create_file(self):
        """
        Create a new file in the current directory
        """
        # 关闭之前的编辑状态
        self.list_view.close_edit()
        
        # Check for duplicate names and generate unique name
        file_name = "New File"
        count = 1
        while any(node.name == file_name for node in self.cur_node.children):
            file_name = f"New File ({count})"
            count += 1
            
        # Create new item
        self.item_1 = QListWidgetItem(QIcon("img/file.png"), file_name)
        self.list_view.addItem(self.item_1)

        # Add to directory tree
        new_node = CatalogNode(file_name, True, self.fat, self.disk, time.localtime(time.time()), self.cur_node)
        self.cur_node.children.append(new_node)
        self.catalog.append(new_node)

        # Update tree
        self.update_tree()
        
        # Set focus and edit
        self.list_view.setCurrentItem(self.item_1)
        self.list_view.setFocus()
        
        # 延迟一下激活编辑，确保UI已更新
        QTimer.singleShot(100, self.list_view.edit_last)

    def view_attribute(self):
        """
        View properties of the selected file or current folder
        """
        # View current directory properties if nothing selected
        if len(self.list_view.selectedItems()) == 0:
            self.child = AttributeForm(self.cur_node.name, False, self.cur_node.create_time, 
                                      self.cur_node.update_time, len(self.cur_node.children))
            self.child.show()
            return
        else:
            # Get the last selected item
            node = self.cur_node.children[self.list_view.selectedIndexes()[-1].row()]
            if node.is_file:
                self.child = AttributeForm(node.name, node.is_file, node.create_time, node.update_time, 0)
            else:
                self.child = AttributeForm(node.name, node.is_file, node.create_time, node.update_time, len(node.children))
            self.child.show()
            return
            
    def getData(self, parameter):
        """
        Write new data to file
        """
        self.write_file.data.update(parameter, self.fat, self.disk)
        self.write_file.update_time = time.localtime(time.time())

    def show_menu(self, point):
        menu = QMenu(self.list_view)
        
        # If items are selected
        if len(self.list_view.selectedItems()) != 0:
            """
            File operations for selected items
            """
            open_file_action = QAction(QIcon(), 'Open')
            open_file_action.triggered.connect(self.open_file)
            menu.addAction(open_file_action)

            delete_action = QAction(QIcon(), 'Delete')
            delete_action.triggered.connect(self.delete_file)
            menu.addAction(delete_action)

            rename_action = QAction(QIcon(), 'Rename')
            rename_action.triggered.connect(self.rename)
            menu.addAction(rename_action)

            view_attribute_action = QAction(QIcon('img/attribute.png'), 'Properties')
            view_attribute_action.triggered.connect(self.view_attribute)
            menu.addAction(view_attribute_action)

            dest_point = self.list_view.mapToGlobal(point)
            menu.exec_(dest_point)

        else:
            """
            View options
            """
            view_menu = QMenu(menu)
            view_menu.setTitle('View')
            
            # Large icons
            big_icon_action = QAction(QIcon(), 'Large Icons')
            def big_icon():
                self.list_view.setIconSize(QSize(172, 172))
                self.list_view.setGridSize(QSize(200, 200))
            big_icon_action.triggered.connect(big_icon)
            view_menu.addAction(big_icon_action)

            # Medium icons
            middle_icon_action = QAction(QIcon(), 'Medium Icons')
            def middle_icon():
                self.list_view.setIconSize(QSize(72, 72))
                self.list_view.setGridSize(QSize(100, 100))
            middle_icon_action.triggered.connect(middle_icon)
            view_menu.addAction(middle_icon_action)

            # Small icons
            small_icon_action = QAction(QIcon(), 'Small Icons')
            def small_icon():
                self.list_view.setIconSize(QSize(56, 56))
                self.list_view.setGridSize(QSize(84, 84))
            small_icon_action.triggered.connect(small_icon)
            view_menu.addAction(small_icon_action)

            menu.addMenu(view_menu)
            
            """
            Create new items
            """
            create_menu = QMenu(menu)
            create_menu.setTitle('New')

            # New folder
            create_folder_action = QAction(QIcon('img/folder.png'), 'Folder')
            create_folder_action.triggered.connect(self.create_folder)
            create_menu.addAction(create_folder_action)

            # New file
            create_file_action = QAction(QIcon('img/file.png'), 'File')
            create_file_action.triggered.connect(self.create_file)
            create_menu.addAction(create_file_action)

            create_menu.setIcon(QIcon('img/create.png'))
            menu.addMenu(create_menu)

            """
            Properties
            """
            view_attribute_action = QAction(QIcon('img/attribute.png'), 'Properties')
            view_attribute_action.triggered.connect(self.view_attribute)
            menu.addAction(view_attribute_action)

            self.next_step = False
            
            dest_point = self.list_view.mapToGlobal(point)
            menu.exec_(dest_point)

    def update_tree(self):
        """
        Update the directory tree after changes
        """
        node = self.root_node
        item = self.root_item

        if item.childCount() < len(node.children):
            # Add a new item
            child = QTreeWidgetItem(item)
        elif item.childCount() > len(node.children):
            # Find and remove the corresponding element
            for i in range(item.childCount()):
                if i == item.childCount() - 1:
                    item.removeChild(item.child(i))
                    break
                if item.child(i).text(0) != node.children[i].name:
                    item.removeChild(item.child(i))
                    break

        for i in range(len(node.children)):
            self.update_tree_recursive(node.children[i], item.child(i))

        self.update_tree_recursive(node, item)

    def update_tree_recursive(self, node: CatalogNode, item: QTreeWidgetItem):
        """
        Recursively update tree items
        """
        item.setText(0, node.name)
        if node.is_file:
            item.setIcon(0, QIcon('img/file.png'))
        else:
            # Set icon based on whether it has children
            if len(node.children) == 0:
                item.setIcon(0, QIcon('img/folder.png'))
            else:
                item.setIcon(0, QIcon('img/folderWithFile.png'))
            if item.childCount() < len(node.children):
                # Add a new item
                child = QTreeWidgetItem(item)
            elif item.childCount() > len(node.children):
                # Find and remove the corresponding element
                for i in range(item.childCount()):
                    if i == item.childCount() - 1:
                        item.removeChild(item.child(i))
                        break
                    if item.child(i).text(0) != node.children[i].name:
                        item.removeChild(item.child(i))
                        break
            for i in range(len(node.children)):
                self.update_tree_recursive(node.children[i], item.child(i))


    def build_tree(self):
        """
        Build the initial directory tree
        """
        self.tree.clear()
        self.root_item = self.build_tree_recursive(self.catalog[0], self.tree)
        # Add root node and its children
        self.tree.addTopLevelItem(self.root_item)
        self.tree.expandAll()
        
    def build_tree_recursive(self, node: CatalogNode, parent: QTreeWidgetItem):
        """
        Build directory tree recursively
        """
        child = QTreeWidgetItem(parent)
        child.setText(0, node.name)

        if node.is_file:
            child.setIcon(0, QIcon('img/file.png'))
        else:
            if len(node.children) == 0:
                child.setIcon(0, QIcon('img/folder.png'))
            else:
                child.setIcon(0, QIcon('img/folderWithFile.png'))
            for i in node.children:
                self.build_tree_recursive(i, child)
        
        return child

    def load_cur_file(self):
        """
        Load files in the current directory
        """
        self.list_view.clear()

        for i in self.cur_node.children:
            if i.is_file:
                # Apply different icons based on filename extension
                icon = self.get_file_icon(i.name)
                self.item_1 = QListWidgetItem(icon, i.name)
            else:
                if len(i.children) == 0:
                    self.item_1 = QListWidgetItem(QIcon("img/folder.png"), i.name)
                else:
                    self.item_1 = QListWidgetItem(QIcon("img/folderWithFile.png"), i.name)
                    
            # Add tooltips with file information
            if i.is_file:
                tooltip = f"File: {i.name}\nCreated: {time.strftime('%Y-%m-%d %H:%M:%S', i.create_time)}"
            else:
                item_count = len(i.children)
                item_text = "items" if item_count != 1 else "item"
                tooltip = f"Folder: {i.name}\nContains: {item_count} {item_text}\nCreated: {time.strftime('%Y-%m-%d %H:%M:%S', i.create_time)}"
            
            self.item_1.setToolTip(tooltip)
            self.list_view.addItem(self.item_1)
            
    def get_file_icon(self, filename):
        """
        Return appropriate icon based on file extension
        """
        # Extract file extension (lowercase)
        _, ext = os.path.splitext(filename.lower())
        
        # Default icon
        icon = QIcon("img/file.png")
        
        # Add more icon mappings as needed
        # This is just a placeholder - ideally you'd have more icons in your img folder
        
        return icon

    def format(self):
        """
        Format the disk (clear all content)
        """ 
        # End editing
        self.list_view.close_edit()

        # Confirmation dialog
        reply = QMessageBox()
        reply.setWindowTitle('Confirm Format')
        reply.setText('Are you sure you want to format the disk? (This operation cannot be undone!)')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        buttonY = reply.button(QMessageBox.Yes)
        buttonY.setText('Yes')
        buttonN = reply.button(QMessageBox.No)
        buttonN.setText('No')

        reply.exec_()

        if reply.clickedButton() == buttonN:
            return
        
        """
        Format the file system
        """
        self.fat = FAT()
        self.fat.fat = [-2] * BLOCK_NUM
        # Save FAT table
        with open('fat', 'wb') as f:
            f.write(pickle.dumps(self.fat))

        self.disk = []
        for i in range(BLOCK_NUM):
            self.disk.append(Block(i))
        # Save disk
        with open('disk', 'wb') as f:
            f.write(pickle.dumps(self.disk))
        
        self.catalog = []
        self.catalog.append(CatalogNode("root", False, self.fat, self.disk, time.localtime(time.time())))
        # Save catalog
        with open('catalog', 'wb') as f:
            f.write(pickle.dumps(self.catalog))

        self.hide()
        self.winform = MainForm()
        self.winform.show()
        
    
    def save_file(self):
        """
        Save files from memory to disk
        """
        # Save FAT table
        with open('fat', 'wb') as f:
            f.write(pickle.dumps(self.fat))
        # Save disk blocks
        with open('disk', 'wb') as f:
            f.write(pickle.dumps(self.disk))
        # Save catalog
        with open('catalog', 'wb') as f:
            f.write(pickle.dumps(self.catalog))

    def read_file(self):
        """
        Read file system data from disk
        """
        # Read FAT table
        if not os.path.exists('fat'):
            self.fat = FAT()
            self.fat.fat = [-2] * BLOCK_NUM
            # Store FAT table
            with open('fat', 'wb') as f:
                f.write(pickle.dumps(self.fat))
        else:
            with open('fat', 'rb') as f:
                self.fat = pickle.load(f)

        # Read disk blocks
        if not os.path.exists('disk'):
            self.disk = []
            for i in range(BLOCK_NUM):
                self.disk.append(Block(i))
            # Store disk table
            with open('disk', 'wb') as f:
                f.write(pickle.dumps(self.disk))
        else:
            with open('disk', 'rb') as f:
                self.disk = pickle.load(f)

        # Read catalog
        if not os.path.exists('catalog'):
            self.catalog = []
            self.catalog.append(CatalogNode("root", False, self.fat, self.disk, time.localtime(time.time())))
            # Store
            with open('catalog', 'wb') as f:
                f.write(pickle.dumps(self.catalog))
        else:
            with open('catalog', 'rb') as f:
                self.catalog = pickle.load(f)
                
            # Handle attribute name changes for backward compatibility
            self.update_attributes_recursive(self.catalog[0])
            
    def update_attributes_recursive(self, node):
        """
        Update attribute names for backward compatibility
        """
        # Handle attribute name changes from 'isFile' to 'is_file'
        if hasattr(node, 'isFile'):
            node.is_file = node.isFile
            
        # Handle attribute name changes from 'createTime' to 'create_time'
        if hasattr(node, 'createTime'):
            node.create_time = node.createTime
            
        # Handle attribute name changes from 'updateTime' to 'update_time'
        if hasattr(node, 'updateTime'):
            node.update_time = node.updateTime
            
        # Recursively update children
        if hasattr(node, 'is_file') and not node.is_file:
            for child in node.children:
                self.update_attributes_recursive(child)

    def initial(self):
        """
        Initialize file system
        """
        # FAT table
        self.fat = FAT()
        self.fat.fat = [-2] * BLOCK_NUM
        # Store FAT table
        with open('fat', 'ab') as f:
            f.write(pickle.dumps(self.fat))
        
        # Disk blocks
        self.disk = []
        for i in range(BLOCK_NUM):
            self.disk.append(Block(i))
        # Store disk table
        with open('disk', 'ab') as f:
            f.write(pickle.dumps(self.disk))
        
        # Catalog node
        self.catalog = []
        self.catalog.append(CatalogNode("root", False, self.fat, self.disk, time.localtime(time.time())))
        # Store
        with open('catalog', 'ab') as f:
            f.write(pickle.dumps(self.catalog))

    
    def back_event(self):
        """
        Navigate to parent directory
        """
        self.list_view.close_edit()

        if self.root_node == self.cur_node:
            # Can't go back from root
            return False

        # Record last position for forward navigation
        for i in range(len(self.cur_node.parent.children)):
            if self.cur_node.parent.children[i].name == self.cur_node.name:
                self.last_loc = i
                self.forward_action.setEnabled(True)
                break

        self.cur_node = self.cur_node.parent
        self.update_loc()
        self.base_url.pop()
        self.tree_item.pop()
        self.tree.setCurrentItem(self.tree_item[-1])
        self.update_tree()
        self.update_print()

        if self.cur_node == self.root_node:
            self.back_action.setEnabled(False)
            
        return True

    def forward_event(self):
        """
        Navigate forward to previously visited location
        """
        self.next_step = True
        self.open_file(QModelIndex())

    def closeEvent(self, event):
        """
        Handle window close event
        """
        # End editing
        self.list_view.close_edit()

        # Confirmation dialog
        reply = QMessageBox()
        reply.setWindowTitle('Save Changes')
        reply.setText('Do you want to save your changes?')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Ignore)
        buttonY = reply.button(QMessageBox.Yes)
        buttonY.setText('Save')
        buttonN = reply.button(QMessageBox.No)
        buttonN.setText('Cancel')
        buttonI = reply.button(QMessageBox.Ignore)
        buttonI.setText('Don\'t Save')

        reply.exec_()

        if reply.clickedButton() == buttonI:
            event.accept()
        elif reply.clickedButton() == buttonY:
            self.save_file()
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainform = MainForm()

    mainform.show()

    sys.exit(app.exec_())

