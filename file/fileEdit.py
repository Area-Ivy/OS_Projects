"""
File editing dialogs for the file management system
"""
import sys
from typing import Optional, Callable
from PyQt5.QtWidgets import (
    QWidget, QTextEdit, QHBoxLayout, QVBoxLayout, QMessageBox,
    QLabel, QGridLayout
)
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import pyqtSignal, Qt
import time


class EditForm(QWidget):
    """
    Dialog for editing file contents
    """
    # Signal to notify parent about content changes
    _signal = pyqtSignal(str)

    def __init__(self, name: str, data: str):
        super().__init__()
        
        # Window setup
        self.resize(1200, 800)
        self.setWindowTitle(name)
        self.name = name
        self.setWindowIcon(QIcon('img/file.png'))
        self.resize(412, 412)
        
        # Text editor setup
        self.text_edit = QTextEdit(self)
        self.text_edit.setText(data)
        self.text_edit.setPlaceholderText("Enter file content here")
        self.text_edit.textChanged.connect(self.change_message)
        self.initial_data = data

        # Layout setup
        self.h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.text_edit)
        self.v_layout.addLayout(self.h_layout)
        self.setLayout(self.v_layout)

        # Make dialog modal
        self.setWindowModality(Qt.ApplicationModal)

    def closeEvent(self, event):
        """
        Handle close event with save prompt if content was modified
        """
        # If no changes were made, just close
        if self.initial_data == self.text_edit.toPlainText():
            event.accept()
            return

        # Show save dialog
        reply = QMessageBox()
        reply.setWindowTitle('Reminder')
        reply.setText(f'Do you want to save changes to {self.name}?')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Ignore)
        
        button_yes = reply.button(QMessageBox.Yes)
        button_yes.setText('Save')
        button_no = reply.button(QMessageBox.No)
        button_no.setText('Don\'t Save')
        button_ignore = reply.button(QMessageBox.Ignore)
        button_ignore.setText('Cancel')

        reply.exec_()

        # Handle user's choice
        if reply.clickedButton() == button_ignore:
            event.ignore()
        elif reply.clickedButton() == button_yes:
            self._signal.emit(self.text_edit.toPlainText())
            event.accept()
        else:
            event.accept()

    def change_message(self):
        """
        Handle text changes in the editor
        """
        pass


class AttributeForm(QWidget):
    """
    Dialog for displaying file or folder attributes
    """
    def __init__(self, name: str, is_file: bool, create_time: time.struct_time, 
                 update_time: time.struct_time, child_count: int = 0):
        super().__init__()
        
        # Window setup
        self.resize(1200, 800)
        self.setWindowTitle('Properties')
        self.name = name
        self.setWindowIcon(QIcon('img/attribute.png'))
        self.resize(412, 412)
        
        # Layout setup
        grid = QGridLayout()

        # Icon based on type
        self.icon = QPixmap('img/file.png' if is_file else 'img/folder.png')
        lbl = QLabel(self)
        lbl.setPixmap(self.icon)
        grid.addWidget(lbl, 0, 0)

        # Font for labels
        font = QFont()
        font.setPointSize(14)

        # File/folder name
        file_name = QLabel(self)
        file_name.setText(f'Name: {self.name}')
        file_name.setFont(font)
        grid.addWidget(file_name, 1, 0)

        # Creation time
        create_label = QLabel(self)
        create_time_str = self._format_time(create_time)
        create_label.setText(f'Created: {create_time_str}')
        create_label.setFont(font)
        grid.addWidget(create_label, 2, 0)

        # Last modified time or item count
        if is_file:
            update_label = QLabel(self)
            update_time_str = self._format_time(update_time)
            update_label.setText(f'Modified: {update_time_str}')
            update_label.setFont(font)
            grid.addWidget(update_label, 3, 0)
        else:
            update_label = QLabel(self)
            update_label.setText(f'Contains {child_count} items')
            update_label.setFont(font)
            grid.addWidget(update_label, 3, 0)

        self.setLayout(grid)
        self.setWindowModality(Qt.ApplicationModal)
    
    def _format_time(self, time_struct: time.struct_time) -> str:
        """
        Format time structure into readable string
        """
        year = str(time_struct.tm_year)
        month = str(time_struct.tm_mon)
        day = str(time_struct.tm_mday)
        hour = str(time_struct.tm_hour).zfill(2)
        minute = str(time_struct.tm_min).zfill(2)
        second = str(time_struct.tm_sec).zfill(2)
        
        return f'{year}-{month}-{day} {hour}:{minute}:{second}'

