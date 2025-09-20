#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Details and Context Menu
Displays detailed photo information and provides context menu actions
"""

import os
import subprocess
import platform
from datetime import datetime
from typing import Optional
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                             QMenu, QAction, QMessageBox, QTextEdit, QTabWidget,
                             QWidget, QScrollArea, QFrame, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QFileInfo, QUrl
from PyQt5.QtGui import QPixmap, QFont, QDesktopServices, QColor

from .photo_scanner import PhotoInfo


class PhotoDetailsDialog(QDialog):
    """Detailed photo information dialog"""
    
    def __init__(self, photo_info: PhotoInfo, parent=None):
        super().__init__(parent)
        self.photo_info = photo_info
        self.setup_ui()
        self.load_photo_data()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("照片详情")
        self.setFixedSize(600, 700)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Photo preview
        self.create_preview_section(layout)
        
        # Tab widget for details
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_basic_info_tab()
        self.create_metadata_tab()
        self.create_file_info_tab()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.open_folder_btn = QPushButton("在资源管理器中打开")
        self.open_folder_btn.clicked.connect(self.open_in_explorer)
        button_layout.addWidget(self.open_folder_btn)
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def create_preview_section(self, layout):
        """Create photo preview section"""
        preview_frame = QFrame()
        preview_frame.setFixedHeight(200)
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 8px;
            }
        """)
        
        preview_layout = QHBoxLayout(preview_frame)
        preview_layout.setAlignment(Qt.AlignCenter)
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMaximumSize(180, 180)
        self.preview_label.setScaledContents(False)  # Change to False to prevent distortion
        self.preview_label.setWordWrap(True)  # Enable word wrap for error texts
        
        # Load thumbnail/preview
        self.load_preview()
        
        preview_layout.addWidget(self.preview_label)
        layout.addWidget(preview_frame)
    
    def create_basic_info_tab(self):
        """Create basic information tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        # Create info grid
        grid = QGridLayout()
        grid.setSpacing(8)
        
        info_items = [
            ("文件名:", self.photo_info.file_name),
            ("格式:", self.photo_info.format),
            ("文件大小:", self.format_file_size(self.photo_info.file_size)),
            ("尺寸:", f"{self.photo_info.width} × {self.photo_info.height}" if self.photo_info.width > 0 else "未知"),
            ("创建时间:", self.format_datetime(self.photo_info.creation_time)),
            ("修改时间:", self.format_datetime(self.photo_info.modification_time)),
            ("文件夹:", os.path.basename(self.photo_info.folder_path)),
        ]
        
        for i, (label_text, value_text) in enumerate(info_items):
            label = QLabel(label_text)
            label.setProperty("labelStyle", "caption")
            label.setMinimumWidth(100)
            
            value = QLabel(str(value_text))
            value.setWordWrap(True)
            
            grid.addWidget(label, i, 0, Qt.AlignTop)
            grid.addWidget(value, i, 1, Qt.AlignTop)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "基本信息")
    
    def create_metadata_tab(self):
        """Create metadata/EXIF tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        if self.photo_info.exif_data:
            # Create table for EXIF data
            table = QTableWidget()
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["属性", "值"])
            table.horizontalHeader().setStretchLastSection(True)
            table.setAlternatingRowColors(True)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            
            # Style the table
            table.setStyleSheet("""
                QTableWidget {
                    background-color: #2d2d2d;
                    alternate-background-color: #353535;
                    gridline-color: #404040;
                    border: 1px solid #404040;
                    border-radius: 6px;
                }
                QTableWidget::item {
                    padding: 4px;
                }
                QHeaderView::section {
                    background-color: #0d7377;
                    color: white;
                    padding: 6px;
                    border: none;
                    font-weight: bold;
                }
            """)
            
            # Add EXIF data
            exif_items = list(self.photo_info.exif_data.items())
            table.setRowCount(len(exif_items))
            
            for i, (key, value) in enumerate(exif_items):
                # Format key
                key_item = QTableWidgetItem(str(key))
                key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable)
                key_item.setForeground(QColor("#0d7377"))  # Teal color for keys
                
                # Format value
                value_str = str(value)
                if len(value_str) > 100:
                    value_str = value_str[:97] + "..."
                
                value_item = QTableWidgetItem(value_str)
                value_item.setFlags(value_item.flags() & ~Qt.ItemIsEditable)
                value_item.setToolTip(str(value))
                
                table.setItem(i, 0, key_item)
                table.setItem(i, 1, value_item)
            
            table.resizeColumnsToContents()
            layout.addWidget(table)
        else:
            # No metadata available
            no_data_label = QLabel("此文件没有可用的元数据。")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setProperty("labelStyle", "caption")
            layout.addWidget(no_data_label)
        
        self.tab_widget.addTab(tab, "元数据")
    
    def create_file_info_tab(self):
        """Create detailed file information tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        # File path section
        path_label = QLabel("完整路径:")
        path_label.setProperty("labelStyle", "caption")
        layout.addWidget(path_label)
        
        path_text = QTextEdit()
        path_text.setPlainText(self.photo_info.file_path)
        path_text.setMaximumHeight(80)
        path_text.setReadOnly(True)
        layout.addWidget(path_text)
        
        # Additional file info
        grid = QGridLayout()
        grid.setSpacing(8)
        
        # Get additional file info
        file_info = QFileInfo(self.photo_info.file_path)
        
        additional_items = [
            ("文件哈希:", self.photo_info.file_hash or "未计算"),
            ("可读:", "是" if file_info.isReadable() else "否"),
            ("可写:", "是" if file_info.isWritable() else "否"),
            ("所有者:", file_info.owner() or "未知"),
            ("组:", file_info.group() or "未知"),
        ]
        
        # Add system-specific info
        if platform.system() == "Windows":
            additional_items.extend([
                ("属性:", self.get_windows_attributes()),
            ])
        
        for i, (label_text, value_text) in enumerate(additional_items):
            label = QLabel(label_text)
            label.setProperty("labelStyle", "caption")
            label.setMinimumWidth(100)
            
            value = QLabel(str(value_text))
            value.setWordWrap(True)
            
            grid.addWidget(label, i, 0, Qt.AlignTop)
            grid.addWidget(value, i, 1, Qt.AlignTop)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "文件信息")
    
    def load_preview(self):
        """Load photo preview"""
        try:
            if not os.path.exists(self.photo_info.file_path):
                self.preview_label.setText("文件不存在")
                return
                
            pixmap = QPixmap(self.photo_info.file_path)
            if not pixmap.isNull():
                # Scale to fit preview maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    180, 180,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled_pixmap)
            else:
                self.preview_label.setText("预览\n不可用")
        except Exception as e:
            self.preview_label.setText(f"预览错误:\n{str(e)[:30]}")
    
    def load_photo_data(self):
        """Load photo data into the dialog"""
        # This method can be extended to load additional data
        pass
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def format_datetime(self, dt: datetime) -> str:
        """Format datetime for display"""
        if dt:
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return "Unknown"
    
    def get_windows_attributes(self) -> str:
        """Get Windows file attributes"""
        try:
            import stat
            file_stat = os.stat(self.photo_info.file_path)
            attrs = []
            
            if file_stat.st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN:
                attrs.append("隐藏")
            if file_stat.st_file_attributes & stat.FILE_ATTRIBUTE_READONLY:
                attrs.append("只读")
            if file_stat.st_file_attributes & stat.FILE_ATTRIBUTE_ARCHIVE:
                attrs.append("存档")
            
            return ", ".join(attrs) if attrs else "普通"
        except:
            return "未知"
    
    def open_in_explorer(self):
        """Open file location in system file explorer"""
        try:
            if platform.system() == "Windows":
                # Windows Explorer - use the correct parameters
                # Make sure the path uses backslashes and exists
                file_path = os.path.normpath(self.photo_info.file_path)
                if os.path.exists(file_path):
                    subprocess.run(["explorer", "/select,", file_path], check=False)
                else:
                    # If file doesn't exist, open the folder
                    folder_path = os.path.dirname(file_path)
                    if os.path.exists(folder_path):
                        subprocess.run(["explorer", folder_path], check=False)
                    else:
                        QMessageBox.warning(self, "错误", "文件或文件夹不存在。")
            elif platform.system() == "Darwin":
                # macOS Finder
                subprocess.run(["open", "-R", self.photo_info.file_path])
            else:
                # Linux file manager
                folder_path = os.path.dirname(self.photo_info.file_path)
                QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开文件位置：{str(e)}")


class PhotoContextMenu(QMenu):
    """Context menu for photo operations"""
    
    # Signals
    show_details = pyqtSignal(PhotoInfo)
    open_photo = pyqtSignal(PhotoInfo)
    copy_path = pyqtSignal(PhotoInfo)
    delete_photo = pyqtSignal(PhotoInfo)
    
    def __init__(self, photo_info: PhotoInfo, parent=None):
        super().__init__(parent)
        self.photo_info = photo_info
        self.setup_menu()
    
    def setup_menu(self):
        """Setup context menu actions"""
        # View details action
        details_action = QAction("查看详情...", self)
        details_action.triggered.connect(lambda: self.show_details.emit(self.photo_info))
        self.addAction(details_action)
        
        self.addSeparator()
        
        # Open photo action
        open_action = QAction("使用默认查看器打开", self)
        open_action.triggered.connect(lambda: self.open_photo.emit(self.photo_info))
        self.addAction(open_action)
        
        # Open in explorer action
        if platform.system() == "Windows":
            explorer_text = "在资源管理器中显示"
        elif platform.system() == "Darwin":
            explorer_text = "在 Finder 中显示"
        else:
            explorer_text = "在文件管理器中显示"
        
        explorer_action = QAction(explorer_text, self)
        explorer_action.triggered.connect(self.open_in_explorer)
        self.addAction(explorer_action)
        
        self.addSeparator()
        
        # Copy path action
        copy_action = QAction("复制文件路径", self)
        copy_action.triggered.connect(lambda: self.copy_path.emit(self.photo_info))
        self.addAction(copy_action)
        
        # Copy name action
        copy_name_action = QAction("复制文件名", self)
        copy_name_action.triggered.connect(self.copy_file_name)
        self.addAction(copy_name_action)
        
        self.addSeparator()
        
        # Delete action
        delete_action = QAction("删除文件...", self)
        delete_action.triggered.connect(lambda: self.delete_photo.emit(self.photo_info))
        self.addAction(delete_action)
    
    def open_in_explorer(self):
        """Open file location in system file explorer"""
        try:
            if platform.system() == "Windows":
                # Windows Explorer - use the correct parameters
                file_path = os.path.normpath(self.photo_info.file_path)
                if os.path.exists(file_path):
                    subprocess.run(["explorer", "/select,", file_path], check=False)
                else:
                    # If file doesn't exist, open the folder
                    folder_path = os.path.dirname(file_path)
                    if os.path.exists(folder_path):
                        subprocess.run(["explorer", folder_path], check=False)
                    else:
                        QMessageBox.warning(self.parent(), "错误", "文件或文件夹不存在。")
            elif platform.system() == "Darwin":
                subprocess.run(["open", "-R", self.photo_info.file_path])
            else:
                folder_path = os.path.dirname(self.photo_info.file_path)
                QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
        except Exception as e:
            QMessageBox.warning(self.parent(), "错误", f"无法打开文件位置：{str(e)}")
    
    def copy_file_name(self):
        """Copy file name to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.photo_info.file_name)


class PhotoOperations:
    """Static class for photo operations"""
    
    @staticmethod
    def show_photo_details(photo_info: PhotoInfo, parent=None):
        """Show photo details dialog"""
        dialog = PhotoDetailsDialog(photo_info, parent)
        dialog.exec_()
    
    @staticmethod
    def open_photo_with_default_viewer(photo_info: PhotoInfo):
        """Open photo with system default viewer"""
        try:
            if platform.system() == "Windows":
                os.startfile(photo_info.file_path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", photo_info.file_path])
            else:
                subprocess.run(["xdg-open", photo_info.file_path])
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Could not open photo: {str(e)}")
    
    @staticmethod
    def copy_file_path_to_clipboard(photo_info: PhotoInfo):
        """Copy file path to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(photo_info.file_path)
    
    @staticmethod
    def delete_photo_file(photo_info: PhotoInfo, parent=None) -> bool:
        """Delete photo file with confirmation"""
        reply = QMessageBox.question(
            parent,
            "删除照片",
            f"确定要删除这张照片吗？\n\n"
            f"文件：{photo_info.file_name}\n"
            f"此操作无法撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                os.remove(photo_info.file_path)
                QMessageBox.information(parent, "成功", "照片已成功删除。")
                return True
            except Exception as e:
                QMessageBox.critical(parent, "错误", f"无法删除照片：{str(e)}")
                return False
        
        return False
    
    @staticmethod
    def create_context_menu(photo_info: PhotoInfo, parent=None) -> PhotoContextMenu:
        """Create and return context menu for photo"""
        menu = PhotoContextMenu(photo_info, parent)
        
        # Connect menu signals to static methods
        menu.show_details.connect(lambda pi: PhotoOperations.show_photo_details(pi, parent))
        menu.open_photo.connect(PhotoOperations.open_photo_with_default_viewer)
        menu.copy_path.connect(PhotoOperations.copy_file_path_to_clipboard)
        menu.delete_photo.connect(lambda pi: PhotoOperations.delete_photo_file(pi, parent))
        
        return menu