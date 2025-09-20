#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Gallery Widget
High-performance photo gallery with lazy loading and virtual scrolling
Optimized for handling thousands of photos efficiently
"""

import math
from typing import List, Optional
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
                             QLabel, QPushButton, QFrame, QGridLayout,
                             QSizePolicy, QMenu, QAction, QMessageBox)
from PyQt5.QtCore import (Qt, QTimer, QRect, QSize, pyqtSignal, QThread,
                          QMutex, QMutexLocker, QPoint)
from PyQt5.QtGui import QPixmap, QFont, QPainter, QColor, QBrush, QPen

from .photo_scanner import PhotoInfo
from .thumbnail_generator import ThumbnailGenerator


class PhotoThumbnail(QLabel):
    """Individual photo thumbnail widget"""
    
    # Signals
    clicked = pyqtSignal(PhotoInfo)
    right_clicked = pyqtSignal(PhotoInfo, 'QPoint')  # Use string to avoid type issues
    double_clicked = pyqtSignal(PhotoInfo)
    
    def __init__(self, photo_info: PhotoInfo, thumbnail_size: int, parent=None):
        super().__init__(parent)
        self.photo_info = photo_info
        self.thumbnail_size = thumbnail_size
        self.is_selected = False
        self.is_hovered = False
        
        self.setup_ui()
        self.create_placeholder()
    
    def setup_ui(self):
        """Setup the thumbnail UI"""
        # Reduce fixed size and standardize the aspect ratio
        padding = 8  # Reduced padding for better spacing
        self.setFixedSize(self.thumbnail_size + padding, self.thumbnail_size + 40)  # Reduced height from +50 to +40
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border-radius: 6px;
                padding: 4px;  /* Reduced padding for better appearance */
            }
        """)
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
    
    def create_placeholder(self):
        """Create placeholder while thumbnail loads"""
        try:
            pixmap = QPixmap(self.thumbnail_size, self.thumbnail_size)
            pixmap.fill(QColor(45, 45, 45))
            
            painter = QPainter(pixmap)
            if not painter.isActive():
                # Fallback to simple placeholder
                self.setText("加载中...")
                return
                
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw loading indicator
            painter.setPen(QPen(QColor(180, 180, 180), 2))
            center = self.thumbnail_size // 2
            painter.drawEllipse(center - 20, center - 20, 40, 40)
            
            # Draw filename
            painter.setPen(QColor(255, 255, 255))
            font = painter.font()
            font.setPixelSize(10)
            painter.setFont(font)
            
            filename = self.photo_info.file_name
            if len(filename) > 20:
                filename = filename[:17] + "..."
            
            text_rect = QRect(0, self.thumbnail_size - 30, self.thumbnail_size, 20)
            painter.drawText(text_rect, Qt.AlignCenter, filename)
            
            if painter.isActive():
                painter.end()
            
            self.setPixmap(pixmap)
        except Exception as e:
            print(f"Warning: Failed to create placeholder: {e}")
            # Fallback to text-based placeholder
            self.setText("加载中...")
    
    def set_thumbnail(self, pixmap: QPixmap):
        """Set the actual thumbnail"""
        if pixmap and not pixmap.isNull():
            # Scale pixmap to fit thumbnail size
            scaled_pixmap = pixmap.scaled(
                self.thumbnail_size, 
                self.thumbnail_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
    
    def set_selected(self, selected: bool):
        """Set selection state"""
        self.is_selected = selected
        self.update_appearance()
    
    def update_appearance(self):
        """Update visual appearance based on state"""
        if self.is_selected:
            self.setStyleSheet("""
                QLabel {
                    background-color: rgba(13, 115, 119, 100);
                    border: 2px solid #0d7377;
                    border-radius: 6px;
                    padding: 4px;
                }
            """)
        elif self.is_hovered:
            self.setStyleSheet("""
                QLabel {
                    background-color: rgba(64, 64, 64, 100);
                    border: 1px solid #808080;
                    border-radius: 6px;
                    padding: 4px;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    border-radius: 6px;
                    padding: 4px;
                }
            """)
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.photo_info)
        elif event.button() == Qt.RightButton:
            self.right_clicked.emit(self.photo_info, event.globalPos())
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click events"""
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit(self.photo_info)
        super().mouseDoubleClickEvent(event)
    
    def enterEvent(self, event):
        """Handle mouse enter events"""
        self.is_hovered = True
        self.update_appearance()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave events"""
        self.is_hovered = False
        self.update_appearance()
        super().leaveEvent(event)


class VirtualScrollGallery(QScrollArea):
    """High-performance virtual scrolling gallery for thousands of photos"""
    
    # Signals
    photo_clicked = pyqtSignal(PhotoInfo)
    photo_right_clicked = pyqtSignal(PhotoInfo, 'QPoint')  # Use string to avoid type issues
    photo_double_clicked = pyqtSignal(PhotoInfo)
    selection_changed = pyqtSignal(list)  # List of selected photos
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.photos: List[PhotoInfo] = []
        self.thumbnail_widgets = {}  # Map photo paths to widgets
        self.selected_photos = set()
        self.visible_range = (0, 0)
        self.thumbnail_size = config.get_thumbnail_size()
        self.columns = 5
        self.row_height = self.thumbnail_size + 40  # Updated to match thumbnail height
        self.max_thumbnails = config.get_max_thumbnails()
        self.debug_mode = False  # Disable debug logging for better performance
        
        self.setup_ui()
        self.setup_thumbnail_generator()
        
        # Viewport update timer
        self.viewport_timer = QTimer()
        self.viewport_timer.timeout.connect(self.update_visible_items)
        self.viewport_timer.setSingleShot(True)
    
    def setup_ui(self):
        """Setup the gallery UI"""
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Content widget
        self.content_widget = QWidget()
        self.setWidget(self.content_widget)
        
        # Layout for thumbnails - optimize spacing for better appearance
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setSpacing(6)  # Reduced from 10 to 6 for tighter layout
        self.grid_layout.setContentsMargins(12, 12, 12, 12)  # Reduced from 20 to 12
        
        # Connect scroll events
        self.verticalScrollBar().valueChanged.connect(self.on_scroll)
        self.horizontalScrollBar().valueChanged.connect(self.on_scroll)
    
    def setup_thumbnail_generator(self):
        """Setup thumbnail generator"""
        self.thumbnail_generator = ThumbnailGenerator(self.config, self)
        self.thumbnail_generator.thumbnail_ready.connect(self.on_thumbnail_ready)
        self.thumbnail_generator.error_occurred.connect(self.on_thumbnail_error)
    
    def set_photos(self, photos: List[PhotoInfo]):
        """Set photos to display"""
        # Clear existing widgets
        self.clear_gallery()
        
        self.photos = photos
        self.selected_photos.clear()
        
        if not photos:
            self.show_empty_state()
            return
        
        # Calculate layout
        self.calculate_layout()
        
        # Create virtual grid
        self.create_virtual_grid()
        
        # Load initial visible thumbnails
        self.update_visible_items()
    
    def create_virtual_grid(self):
        """Create virtual grid structure"""
        # This creates the basic grid structure without actually creating all widgets
        # Widgets will be created on-demand as they become visible
        pass
    
    def update_visible_items(self):
        """Update visible thumbnail items"""
        if not self.photos:
            return
        
        # Calculate visible range
        viewport_rect = self.viewport().rect()
        scroll_value = self.verticalScrollBar().value()
        
        # Print viewport information for debugging (only if debug mode is enabled)
        if self.debug_mode:
            print(f"Viewport size: {viewport_rect.width()}x{viewport_rect.height()}, scroll: {scroll_value}")
        
        # Calculate which rows are visible
        first_visible_row = max(0, (scroll_value - 100) // self.row_height)
        last_visible_row = min(self.rows - 1, 
                              (scroll_value + viewport_rect.height() + 100) // self.row_height)
        
        # Calculate photo indices
        start_index = first_visible_row * self.columns
        end_index = min(len(self.photos), (last_visible_row + 1) * self.columns)
        
        # Print visibility range (only if debug mode is enabled)
        if self.debug_mode:
            print(f"Visible rows: {first_visible_row} to {last_visible_row}, indices: {start_index} to {end_index}")
        
        # If the visible range hasn't changed significantly, don't update
        if self.visible_range and (
            abs(start_index - self.visible_range[0]) < self.columns * 2 and
            abs(end_index - self.visible_range[1]) < self.columns * 2
        ):
            if self.debug_mode:
                print("Skipping update - visible range hasn't changed enough")
            return
            
        self.visible_range = (start_index, end_index)
        
        # Create/update visible thumbnails
        self.create_visible_thumbnails(start_index, end_index)
        
        # Remove thumbnails that are no longer visible
        self.cleanup_invisible_thumbnails(start_index, end_index)
    
    def create_visible_thumbnails(self, start_index: int, end_index: int):
        """Create thumbnail widgets for visible photos"""
        thumbnail_requests = []
        
        # Increase the batch size for better performance
        max_new_thumbnails = 30
        count = 0
        
        # Print visibility information for debugging (only if debug mode is enabled)
        if self.debug_mode:
            print(f"Creating visible thumbnails from {start_index} to {end_index}")
        
        for i in range(start_index, end_index):
            if i >= len(self.photos):
                break
            
            photo = self.photos[i]
            
            if photo.file_path not in self.thumbnail_widgets:
                # Create thumbnail widget
                thumbnail = PhotoThumbnail(photo, self.thumbnail_size, self)
                thumbnail.clicked.connect(self.on_photo_clicked)
                thumbnail.right_clicked.connect(self.on_photo_right_clicked)
                thumbnail.double_clicked.connect(self.on_photo_double_clicked)
                
                # Calculate grid position
                row = i // self.columns
                col = i % self.columns
                
                # Add to layout
                self.grid_layout.addWidget(thumbnail, row, col)
                
                # Store widget
                self.thumbnail_widgets[photo.file_path] = thumbnail
                
                # Request thumbnail generation
                thumbnail_requests.append(photo.file_path)
                
                count += 1
                if count >= max_new_thumbnails:
                    break
        
        # Request thumbnails in batch
        if thumbnail_requests:
            if self.debug_mode:
                print(f"Requesting {len(thumbnail_requests)} thumbnails")
            self.thumbnail_generator.request_thumbnails_batch(thumbnail_requests, self.thumbnail_size)
    
    def clear_gallery(self):
        """Clear all thumbnail widgets"""
        for widget in self.thumbnail_widgets.values():
            widget.deleteLater()
        self.thumbnail_widgets.clear()
        
        # Clear layout
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    self.grid_layout.removeWidget(widget)
                    widget.deleteLater()
    
    def show_empty_state(self):
        """Show empty state when no photos"""
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        empty_label = QLabel("未找到照片")
        empty_label.setProperty("labelStyle", "heading")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_label)
        
        desc_label = QLabel("在配置的目录中添加照片或在设置中更改照片路径。")
        desc_label.setProperty("labelStyle", "caption")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        empty_layout.addWidget(desc_label)
        
        self.grid_layout.addWidget(empty_widget, 0, 0, 1, self.columns)
    
    def calculate_layout(self):
        """Calculate grid layout based on available space"""
        if not self.photos:
            return
        
        # Calculate columns based on widget width with adjusted spacing
        padding = 6  # Match grid layout spacing
        margins = 24  # Account for left and right margins (12 * 2)
        available_width = self.viewport().width() - margins
        
        # Calculate item width based on thumbnail size plus padding
        item_width = self.thumbnail_size + padding + 8  # thumbnail + grid spacing + label padding
        
        # Calculate optimal number of columns
        self.columns = max(1, int(available_width / item_width))
        
        # Update row height calculation
        self.row_height = self.thumbnail_size + 40  # Match the thumbnail widget height
        
        # Calculate number of rows
        self.rows = math.ceil(len(self.photos) / self.columns)
        
        # Update content widget size
        content_height = self.rows * self.row_height + margins
        self.content_widget.setFixedHeight(content_height)
    
    def cleanup_invisible_thumbnails(self, start_index: int, end_index: int):
        """Remove thumbnail widgets that are no longer visible"""
        # Keep a buffer of thumbnails around the visible area
        buffer = self.columns * 3
        buffer_start = max(0, start_index - buffer)
        buffer_end = min(len(self.photos), end_index + buffer)
        
        # Limit the number of active thumbnails to prevent memory issues
        max_thumbnails = self.max_thumbnails
        current_count = len(self.thumbnail_widgets)
        
        if current_count > max_thumbnails:
            # Only keep the most relevant thumbnails
            visible_paths = {self.photos[i].file_path for i in range(start_index, end_index) 
                           if i < len(self.photos)}
            
            # Create a list of paths to remove
            paths_to_remove = []
            for photo_path, widget in self.thumbnail_widgets.items():
                # Find photo index
                photo_index = next((i for i, p in enumerate(self.photos) 
                                  if p.file_path == photo_path), -1)
                
                if photo_path not in visible_paths and (
                    photo_index < buffer_start or 
                    photo_index >= buffer_end or 
                    current_count > max_thumbnails
                ):
                    paths_to_remove.append(photo_path)
                    current_count -= 1
                    if current_count <= max_thumbnails:
                        break
            
            # Remove widgets
            for photo_path in paths_to_remove:
                widget = self.thumbnail_widgets.pop(photo_path)
                self.grid_layout.removeWidget(widget)
                widget.deleteLater()
    
    def on_scroll(self):
        """Handle scroll events"""
        # Use timer to avoid too frequent updates - increased from 50ms to 100ms
        self.viewport_timer.start(100)
    
    def on_thumbnail_ready(self, file_path: str, pixmap: QPixmap):
        """Handle thumbnail generation completion"""
        if file_path in self.thumbnail_widgets:
            try:
                widget = self.thumbnail_widgets[file_path]
                if not pixmap.isNull():
                    widget.set_thumbnail(pixmap)
                else:
                    print(f"Received null pixmap for {file_path}")
            except Exception as e:
                print(f"Error setting thumbnail: {e}")
                # If an error occurs, try to show error state
                widget = self.thumbnail_widgets.get(file_path)
                if widget:
                    widget.setText("加载失败")
    
    def on_thumbnail_error(self, error_msg: str, file_path: str):
        """Handle thumbnail generation errors"""
        # Update the placeholder with error message
        if file_path in self.thumbnail_widgets:
            widget = self.thumbnail_widgets[file_path]
            widget.setText("加载失败")
            print(f"Thumbnail error for {file_path}: {error_msg}")
    
    def on_photo_clicked(self, photo_info: PhotoInfo):
        """Handle photo click"""
        # Toggle selection
        if photo_info.file_path in self.selected_photos:
            self.selected_photos.remove(photo_info.file_path)
        else:
            self.selected_photos.add(photo_info.file_path)
        
        # Update visual state
        if photo_info.file_path in self.thumbnail_widgets:
            widget = self.thumbnail_widgets[photo_info.file_path]
            widget.set_selected(photo_info.file_path in self.selected_photos)
        
        self.photo_clicked.emit(photo_info)
        self.selection_changed.emit(list(self.selected_photos))
    
    def on_photo_right_clicked(self, photo_info: PhotoInfo, position: QPoint):
        """Handle photo right click"""
        self.photo_right_clicked.emit(photo_info, position)
    
    def on_photo_double_clicked(self, photo_info: PhotoInfo):
        """Handle photo double click"""
        self.photo_double_clicked.emit(photo_info)
    
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        
        # Recalculate layout
        old_columns = self.columns
        self.calculate_layout()
        
        if old_columns != self.columns and self.photos:
            # Layout changed, need to recreate grid
            self.clear_gallery()
            self.create_virtual_grid()
            self.update_visible_items()
    
    def set_thumbnail_size(self, size: int):
        """Update thumbnail size"""
        self.thumbnail_size = size
        self.row_height = size + 40  # Updated to match thumbnail height
        
        # Clear and recreate with new size
        if self.photos:
            self.clear_gallery()
            self.calculate_layout()
            self.create_virtual_grid()
            self.update_visible_items()
    
    def select_all(self):
        """Select all photos"""
        self.selected_photos = {photo.file_path for photo in self.photos}
        
        # Update visual state for visible widgets
        for widget in self.thumbnail_widgets.values():
            widget.set_selected(True)
        
        self.selection_changed.emit(list(self.selected_photos))
    
    def clear_selection(self):
        """Clear photo selection"""
        self.selected_photos.clear()
        
        # Update visual state for visible widgets
        for widget in self.thumbnail_widgets.values():
            widget.set_selected(False)
        
        self.selection_changed.emit([])
    
    def get_selected_photos(self) -> List[PhotoInfo]:
        """Get currently selected photos"""
        return [photo for photo in self.photos 
                if photo.file_path in self.selected_photos]


class PhotoGalleryWidget(QWidget):
    """Main photo gallery widget with controls"""
    
    # Signals
    photo_clicked = pyqtSignal(PhotoInfo)
    photo_right_clicked = pyqtSignal(PhotoInfo, 'QPoint')  # Use string to avoid type issues
    photo_double_clicked = pyqtSignal(PhotoInfo)
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the gallery UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Gallery controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(16, 8, 16, 8)
        
        self.photo_count_label = QLabel("0 张照片")
        self.photo_count_label.setProperty("labelStyle", "caption")
        controls_layout.addWidget(self.photo_count_label)
        
        controls_layout.addStretch()
        
        # Selection controls
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.setProperty("buttonStyle", "secondary")
        self.select_all_btn.clicked.connect(self.select_all_photos)
        controls_layout.addWidget(self.select_all_btn)
        
        self.clear_selection_btn = QPushButton("清除选择")
        self.clear_selection_btn.setProperty("buttonStyle", "secondary")
        self.clear_selection_btn.clicked.connect(self.clear_selection)
        controls_layout.addWidget(self.clear_selection_btn)
        
        layout.addLayout(controls_layout)
        
        # Gallery
        self.gallery = VirtualScrollGallery(self.config, self)
        self.gallery.photo_clicked.connect(self.photo_clicked)
        self.gallery.photo_right_clicked.connect(self.photo_right_clicked)
        self.gallery.photo_double_clicked.connect(self.photo_double_clicked)
        self.gallery.selection_changed.connect(self.on_selection_changed)
        
        layout.addWidget(self.gallery)
    
    def set_photos(self, photos: List[PhotoInfo]):
        """Set photos to display"""
        self.gallery.set_photos(photos)
        self.update_photo_count(len(photos))
    
    def update_photo_count(self, count: int):
        """Update photo count display"""
        if count == 1:
            self.photo_count_label.setText("1 张照片")
        else:
            self.photo_count_label.setText(f"{count:,} 张照片")
    
    def on_selection_changed(self, selected_paths: List[str]):
        """Handle selection changes"""
        count = len(selected_paths)
        if count == 0:
            self.photo_count_label.setText(f"{len(self.gallery.photos):,} 张照片")
        elif count == 1:
            self.photo_count_label.setText("已选择 1 张照片")
        else:
            self.photo_count_label.setText(f"已选择 {count} 张照片")
    
    def select_all_photos(self):
        """Select all photos"""
        self.gallery.select_all()
    
    def clear_selection(self):
        """Clear photo selection"""
        self.gallery.clear_selection()
    
    def set_thumbnail_size(self, size: int):
        """Update thumbnail size"""
        self.gallery.set_thumbnail_size(size)