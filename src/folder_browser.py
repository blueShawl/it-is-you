#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Folder Tree View Widget
Hierarchical folder view for browsing photos by directory structure
"""

import os
from typing import List, Dict, Optional
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget,
                             QTreeWidgetItem, QLabel, QPushButton, QLineEdit,
                             QSplitter, QFrame, QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont

from .photo_scanner import PhotoInfo
from .photo_gallery import PhotoGalleryWidget


class FolderTreeItem(QTreeWidgetItem):
    """Custom tree item for folders"""
    
    def __init__(self, folder_path: str, photo_count: int, parent=None):
        super().__init__(parent)
        self.folder_path = folder_path
        self.photo_count = photo_count
        
        # Set display text
        folder_name = os.path.basename(folder_path) or folder_path
        self.setText(0, folder_name)
        self.setText(1, str(photo_count))
        
        # Set tooltip
        self.setToolTip(0, folder_path)
        self.setToolTip(1, f"此文件夹中有 {photo_count} 张照片")
        
        # Set data
        self.setData(0, Qt.UserRole, folder_path)


class FolderTreeWidget(QTreeWidget):
    """Tree widget for folder navigation"""
    
    # Signals
    folder_selected = pyqtSignal(str, list)  # folder_path, photos
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.photos_by_folder: Dict[str, List[PhotoInfo]] = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the tree widget"""
        # Configure headers
        self.setHeaderLabels(["文件夹", "照片数"])
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        # Configure appearance
        self.setAlternatingRowColors(True)
        self.setRootIsDecorated(True)
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.AscendingOrder)
        
        # Connect signals
        self.itemClicked.connect(self.on_item_clicked)
        self.itemExpanded.connect(self.on_item_expanded)
    
    def set_photos(self, photos: List[PhotoInfo]):
        """Set photos and build folder tree"""
        self.clear()
        self.photos_by_folder.clear()
        
        if not photos:
            return
        
        # Group photos by folder
        folder_counts = {}
        for photo in photos:
            folder = photo.folder_path
            if folder not in self.photos_by_folder:
                self.photos_by_folder[folder] = []
            self.photos_by_folder[folder].append(photo)
            folder_counts[folder] = folder_counts.get(folder, 0) + 1
        
        # Build folder hierarchy
        self.build_folder_tree(folder_counts)
    
    def build_folder_tree(self, folder_counts: Dict[str, int]):
        """Build hierarchical folder tree"""
        # Get all unique folder paths
        all_folders = set(folder_counts.keys())
        
        # Add parent folders that might not have photos directly
        parent_folders = set()
        for folder in all_folders:
            current = folder
            while current and current != os.path.dirname(current):
                parent = os.path.dirname(current)
                if parent and parent not in all_folders:
                    parent_folders.add(parent)
                current = parent
        
        # Combine all folders
        all_folders.update(parent_folders)
        
        # Create tree structure
        folder_items = {}
        root_folders = set()
        
        # Sort folders by depth (shallower first)
        sorted_folders = sorted(all_folders, key=lambda x: x.count(os.sep))
        
        for folder in sorted_folders:
            photo_count = folder_counts.get(folder, 0)
            
            # Calculate total count including subfolders
            total_count = self.calculate_total_count(folder, folder_counts)
            
            parent_folder = os.path.dirname(folder)
            
            if parent_folder in folder_items:
                # Add as child
                parent_item = folder_items[parent_folder]
                item = FolderTreeItem(folder, total_count, parent_item)
            else:
                # Add as root item
                item = FolderTreeItem(folder, total_count, self)
                root_folders.add(folder)
            
            folder_items[folder] = item
            
            # Expand item if it has photos directly
            if photo_count > 0:
                item.setExpanded(True)
        
        # Expand root items
        for folder in root_folders:
            if folder in folder_items:
                folder_items[folder].setExpanded(True)
    
    def calculate_total_count(self, folder: str, folder_counts: Dict[str, int]) -> int:
        """Calculate total photo count including subfolders"""
        total = folder_counts.get(folder, 0)
        
        # Add counts from subfolders
        for other_folder, count in folder_counts.items():
            if other_folder.startswith(folder + os.sep):
                total += count
        
        return total
    
    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click"""
        if isinstance(item, FolderTreeItem):
            folder_path = item.folder_path
            photos = self.photos_by_folder.get(folder_path, [])
            self.folder_selected.emit(folder_path, photos)
    
    def on_item_expanded(self, item: QTreeWidgetItem):
        """Handle item expansion"""
        # Could implement lazy loading here if needed
        pass


class FolderBrowserWidget(QWidget):
    """Complete folder browsing widget with tree and gallery"""
    
    # Signals
    photo_clicked = pyqtSignal(PhotoInfo)
    photo_right_clicked = pyqtSignal(PhotoInfo, 'QPoint')  # Use string to avoid type issues
    photo_double_clicked = pyqtSignal(PhotoInfo)
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.current_folder = ""
        self.all_photos: List[PhotoInfo] = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the folder browser UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header with improved styling
        header_frame = QFrame()
        header_frame.setProperty("headerFrame", True)
        header_frame.setFixedHeight(60)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 12, 20, 12)
        
        # Title with icon
        title_layout = QHBoxLayout()
        title_label = QLabel("📁 按文件夹浏览")
        title_label.setProperty("labelStyle", "heading")
        title_layout.addWidget(title_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Breadcrumb with better styling
        self.breadcrumb_label = QLabel("")
        self.breadcrumb_label.setProperty("labelStyle", "breadcrumb")
        self.breadcrumb_label.setWordWrap(True)
        self.breadcrumb_label.setMaximumWidth(400)
        header_layout.addWidget(self.breadcrumb_label)
        
        layout.addWidget(header_frame)
        
        # Main content - improved splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        layout.addWidget(splitter)
        
        # Left panel - folder tree with better styling
        left_panel = QFrame()
        left_panel.setProperty("sidePanel", True)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(12, 12, 8, 12)
        left_layout.setSpacing(8)
        
        # Tree header with stats
        tree_header_layout = QHBoxLayout()
        tree_header = QLabel("📂 文件夹")
        tree_header.setProperty("labelStyle", "subheading")
        tree_header_layout.addWidget(tree_header)
        
        # Stats label
        self.folder_stats_label = QLabel("")
        self.folder_stats_label.setProperty("labelStyle", "caption")
        tree_header_layout.addStretch()
        tree_header_layout.addWidget(self.folder_stats_label)
        
        left_layout.addLayout(tree_header_layout)
        
        # Folder tree
        self.folder_tree = FolderTreeWidget()
        self.folder_tree.folder_selected.connect(self.on_folder_selected)
        left_layout.addWidget(self.folder_tree)
        
        left_panel.setMaximumWidth(400)
        left_panel.setMinimumWidth(250)
        splitter.addWidget(left_panel)
        
        # Right panel - photo gallery with better styling
        right_panel = QFrame()
        right_panel.setProperty("mainPanel", True)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 12, 12, 12)
        right_layout.setSpacing(12)
        
        # Gallery header with controls
        gallery_header_layout = QHBoxLayout()
        
        self.gallery_header = QLabel("🖼️ 选择文件夹查看照片")
        self.gallery_header.setProperty("labelStyle", "subheading")
        gallery_header_layout.addWidget(self.gallery_header)
        
        gallery_header_layout.addStretch()
        
        # View options
        self.view_mode_label = QLabel("查看模式：")
        self.view_mode_label.setProperty("labelStyle", "caption")
        gallery_header_layout.addWidget(self.view_mode_label)
        
        right_layout.addLayout(gallery_header_layout)
        
        # Photo gallery
        self.gallery = PhotoGalleryWidget(self.config)
        self.gallery.photo_clicked.connect(self.photo_clicked)
        self.gallery.photo_right_clicked.connect(self.photo_right_clicked)
        self.gallery.photo_double_clicked.connect(self.photo_double_clicked)
        right_layout.addWidget(self.gallery)
        
        splitter.addWidget(right_panel)
        
        # Set splitter proportions (30% left, 70% right)
        splitter.setSizes([300, 700])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
    
    def set_photos(self, photos: List[PhotoInfo]):
        """Set photos and update folder tree"""
        self.all_photos = photos
        self.folder_tree.set_photos(photos)
        
        # Update stats
        folder_count = len(self.folder_tree.photos_by_folder)
        self.folder_stats_label.setText(f"{folder_count} 个文件夹")
        
        # Clear gallery until folder is selected
        self.gallery.set_photos([])
        self.gallery_header.setText("🖼️ 选择文件夹查看照片")
        self.breadcrumb_label.setText("")
    
    def on_folder_selected(self, folder_path: str, photos: List[PhotoInfo]):
        """Handle folder selection"""
        self.current_folder = folder_path
        
        # Update gallery
        self.gallery.set_photos(photos)
        
        # Update header with better formatting
        folder_name = os.path.basename(folder_path) or folder_path
        photo_count = len(photos)
        
        if photo_count == 0:
            self.gallery_header.setText(f"🖼️ {folder_name} - 没有照片")
        elif photo_count == 1:
            self.gallery_header.setText(f"🖼️ {folder_name} - 1 张照片")
        else:
            self.gallery_header.setText(f"🖼️ {folder_name} - {photo_count:,} 张照片")
        
        # Update breadcrumb
        self.update_breadcrumb(folder_path)
    
    def update_breadcrumb(self, folder_path: str):
        """Update breadcrumb navigation"""
        if not folder_path:
            self.breadcrumb_label.setText("")
            return
        
        # Shorten path if too long
        if len(folder_path) > 60:
            parts = folder_path.split(os.sep)
            if len(parts) > 3:
                shortened = f"{parts[0]}{os.sep}...{os.sep}{parts[-2]}{os.sep}{parts[-1]}"
            else:
                shortened = folder_path
        else:
            shortened = folder_path
        
        self.breadcrumb_label.setText(shortened)
    
    def get_current_folder(self) -> str:
        """Get currently selected folder"""
        return self.current_folder
    
    def get_current_photos(self) -> List[PhotoInfo]:
        """Get photos in currently selected folder"""
        if self.current_folder and self.current_folder in self.folder_tree.photos_by_folder:
            return self.folder_tree.photos_by_folder[self.current_folder]
        return []
    
    def set_thumbnail_size(self, size: int):
        """Update thumbnail size"""
        self.gallery.set_thumbnail_size(size)