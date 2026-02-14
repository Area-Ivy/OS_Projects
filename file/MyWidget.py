"""
Custom list widget implementation with drag-and-drop support and file editing capabilities
"""
from typing import Optional, Any, List
from PyQt5.QtWidgets import QListWidget, QWidget, QAbstractItemView, QListWidgetItem, QLineEdit, QMessageBox
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QDragMoveEvent, QKeyEvent
from PyQt5.QtCore import Qt, QModelIndex, QTimer, pyqtSignal

from File import CatalogNode


class MyListWidget(QListWidget):
    """
    Enhanced QListWidget with drag-and-drop support and file editing capabilities
    """
    # 自定义信号，用于通知编辑完成
    editingFinished = pyqtSignal(QListWidgetItem, str)
    
    def __init__(self, cur_node: CatalogNode, parents: Any, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        # Drag and drop settings
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDefaultDropAction(Qt.CopyAction)
        
        # Enable editing
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Current directory and parent reference
        self.cur_node = cur_node
        self.parents = parents
        
        # Editing state
        self.edited_item = None
        self.is_edit = False
        self.editing_index = -1
        
        # 连接信号
        self.itemChanged.connect(self.on_item_changed)
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events"""
        if event.key() == Qt.Key_Return and self.state() == QAbstractItemView.EditingState:
            # 确认编辑
            self.close_edit()
            event.accept()
        elif event.key() == Qt.Key_Escape and self.state() == QAbstractItemView.EditingState:
            # 取消编辑
            self.cancel_edit()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def on_item_changed(self, item):
        """处理项目变更事件"""
        if self.is_edit and self.edited_item == item:
            # 获取新的名称
            new_name = item.text().strip()
            
            # 如果名称为空，设置为默认名称
            if not new_name:
                if self.cur_node.children[self.editing_index].is_file:
                    new_name = "New File"
                else:
                    new_name = "New Folder"
                item.setText(new_name)
            
            # 更新节点名称
            if self.editing_index >= 0 and self.editing_index < len(self.cur_node.children):
                # 检查重名
                original_name = self.cur_node.children[self.editing_index].name
                
                # 如果名称没变，不处理
                if new_name == original_name:
                    return
                
                # 检查是否有重名
                count = 1
                base_name = new_name
                while any(node.name == new_name and node != self.cur_node.children[self.editing_index] 
                          for node in self.cur_node.children):
                    new_name = f"{base_name} ({count})"
                    count += 1
                
                # 如果因为重名修改了名称，更新列表项
                if new_name != item.text():
                    item.setText(new_name)
                
                # 更新节点名称
                self.cur_node.children[self.editing_index].name = new_name
                
                # 更新树视图
                self.parents.update_tree()

    def edit_last(self):
        """编辑最后一个项目"""
        if self.count() == 0:
            return
            
        self.close_edit()  # 先关闭之前的编辑
        self.editing_index = len(self.cur_node.children) - 1
        item = self.item(self.count() - 1)
        self.edited_item = item
        self.is_edit = True
        item.setFlags(item.flags() | Qt.ItemIsEditable)  # 临时可编辑
        self.setCurrentItem(item)
        item.setSelected(True)  # 强制选中
        self.setFocus()         # 强制获得焦点
        self.editItem(item)
        
        # 使用计时器确保编辑状态持续
        QTimer.singleShot(100, lambda: self._resize_editor(item))
    
    def edit_selected(self, index):
        """编辑选中的项目"""
        if index < 0 or index >= self.count():
            return
        self.close_edit()
        item = self.item(index)
        self.editing_index = index
        self.edited_item = item
        self.is_edit = True
        self.setCurrentItem(item)
        item.setSelected(True)  # 强制选中
        item.setFlags(item.flags() | Qt.ItemIsEditable)  # 临时可编辑
        self.setFocus()         # 强制获得焦点
        QTimer.singleShot(0, lambda: self.editItem(item))
        QTimer.singleShot(100, lambda: self._resize_editor(item))
    
    def _resize_editor(self, item):
        """调整编辑框宽高以适应文件名"""
        editor = self.indexWidget(self.indexFromItem(item))
        if editor is None:
            # 兼容标准编辑器
            for child in self.findChildren(QLineEdit):
                if child.isVisible():
                    editor = child
                    break
        if editor:
            editor.setMinimumWidth(120)
            editor.setMaximumWidth(300)
            editor.setFixedWidth(min(max(120, self.visualItemRect(item).width()), 300))
            editor.setFixedHeight(32)  # 设置合适的高度
    
    def close_edit(self):
        """结束编辑"""
        if self.state() == QAbstractItemView.EditingState:
            self.closePersistentEditor(self.currentItem())
            
        # 编辑结束后恢复不可编辑
        if self.is_edit and self.edited_item:
            self.edited_item.setFlags(self.edited_item.flags() & ~Qt.ItemIsEditable)
        
        # 清理编辑状态
        if self.is_edit:
            self.is_edit = False
            self.edited_item = None
            self.editing_index = -1
    
    def cancel_edit(self):
        """取消编辑"""
        if self.state() == QAbstractItemView.EditingState:
            self.closePersistentEditor(self.currentItem())
        
        # 如果是取消编辑，恢复原始名称
        if self.is_edit and self.edited_item and self.editing_index >= 0:
            if self.editing_index < len(self.cur_node.children):
                self.edited_item.setText(self.cur_node.children[self.editing_index].name)
        
        # 清理编辑状态
        self.is_edit = False
        self.edited_item = None
        self.editing_index = -1

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter events from external or internal sources"""
        if event.mimeData().hasText():
            if event.mimeData().text().startswith('file:///'):
                event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        """Handle drag move events"""
        event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop events by adding items to the list"""
        paths = event.mimeData().text().split('\n')
        for path in paths:
            path = path.strip()
            if len(path) > 8:
                self.addItem(path.strip()[8:])
        event.accept()
        
    def addItem(self, *args, **kwargs):
        """Override addItem to make items editable"""
        super().addItem(*args, **kwargs)
        # 不再自动设置为可编辑

