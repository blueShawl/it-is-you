#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Window
The main application window that coordinates all components
"""

import os
from typing import List, Optional
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QStatusBar, QMenuBar, QMenu, QAction,
                             QToolBar, QProgressBar, QLabel, QPushButton,
                             QMessageBox, QSplashScreen, QApplication)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont

from .config import Config
from .styles import apply_theme
from .settings_window import SettingsWindow, FirstRunDialog
from .photo_scanner import PhotoScanner, PhotoDatabase, PhotoInfo
from .photo_gallery import PhotoGalleryWidget
from .folder_browser import FolderBrowserWidget
from .photo_details import PhotoOperations
from .thumbnail_generator import ThumbnailGenerator


class ScanProgressWidget(QWidget):
    """Widget to show scanning progress"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup progress UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)
        
        # Progress info
        self.status_label = QLabel("准备扫描...")
        self.status_label.setProperty("labelStyle", "subheading")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(400)
        layout.addWidget(self.progress_bar)
        
        # Details
        self.details_label = QLabel("")
        self.details_label.setProperty("labelStyle", "caption")
        self.details_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.details_label)
        
        # Cancel button
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setProperty("buttonStyle", "secondary")
        layout.addWidget(self.cancel_button)
    
    def update_progress(self, current: int, total: int, status: str = ""):
        """Update progress display"""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.details_label.setText(f"已处理 {current:,} / {total:,} 个文件")
        
        if status:
            self.status_label.setText(status)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.photo_database = PhotoDatabase()
        self.photo_scanner = None
        self.thumbnail_generator = None
        
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_tool_bar()
        self.setup_status_bar()
        self.connect_signals()
        self.restore_window_state()
        
        # Apply theme
        self.apply_current_theme()
        
        # Initialize components
        self.setup_scanner()
        
        # Check for first run or start scanning
        QTimer.singleShot(500, self.handle_startup)
    
    def setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle("现代照片查看器")
        self.setMinimumSize(1200, 800)
        
        # Central widget with tabs
        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)
        
        # Gallery tab
        self.gallery_tab = PhotoGalleryWidget(self.config)
        self.gallery_tab.photo_clicked.connect(self.on_photo_clicked)
        self.gallery_tab.photo_right_clicked.connect(self.on_photo_right_clicked)
        self.gallery_tab.photo_double_clicked.connect(self.on_photo_double_clicked)
        self.central_widget.addTab(self.gallery_tab, "所有照片")
        
        # Folder browser tab
        self.folder_tab = FolderBrowserWidget(self.config)
        self.folder_tab.photo_clicked.connect(self.on_photo_clicked)
        self.folder_tab.photo_right_clicked.connect(self.on_photo_right_clicked)
        self.folder_tab.photo_double_clicked.connect(self.on_photo_double_clicked)
        self.central_widget.addTab(self.folder_tab, "按文件夹浏览")
        
        # Progress widget (hidden initially)
        self.progress_widget = ScanProgressWidget()
        self.progress_widget.cancel_button.clicked.connect(self.cancel_scanning)
        
        # Initially show progress if no photos
        if not self.config.get_photo_path():
            self.central_widget.addTab(self.progress_widget, "Scanning...")
            self.central_widget.setCurrentWidget(self.progress_widget)
    
    def setup_menu_bar(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("文件")
        
        self.scan_action = QAction("扫描照片", self)
        self.scan_action.setShortcut("Ctrl+R")
        self.scan_action.triggered.connect(self.start_scanning)
        file_menu.addAction(self.scan_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction("设置...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(lambda: self.close())
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("查看")
        
        self.theme_action = QAction("切换主题", self)
        self.theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.theme_action)
        
        view_menu.addSeparator()
        
        refresh_action = QAction("刷新", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_view)
        view_menu.addAction(refresh_action)
        
        # Help menu
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_tool_bar(self):
        """Setup tool bar"""
        toolbar = self.addToolBar("MainToolBar")
        toolbar.setObjectName("MainToolBar")  # Set object name to avoid warnings
        toolbar.setMovable(False)
        
        # Scan button
        self.scan_button = QPushButton("扫描照片")
        self.scan_button.clicked.connect(self.start_scanning)
        toolbar.addWidget(self.scan_button)
        
        toolbar.addSeparator()
        
        # Settings button
        settings_button = QPushButton("设置")
        settings_button.clicked.connect(self.show_settings)
        toolbar.addWidget(settings_button)
        
        toolbar.addSeparator()
        
        # Photo count label
        self.photo_count_label = QLabel("0 张照片")
        self.photo_count_label.setProperty("labelStyle", "caption")
        toolbar.addWidget(self.photo_count_label)
        
        # Add stretch to push items to the right
        spacer = QWidget()
        spacer.setSizePolicy(toolbar.sizePolicy().Expanding, toolbar.sizePolicy().Preferred)
        toolbar.addWidget(spacer)
        
        # Theme toggle
        theme_button = QPushButton("切换主题")
        theme_button.clicked.connect(self.toggle_theme)
        toolbar.addWidget(theme_button)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status label
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        
        # Progress bar for operations
        self.operation_progress = QProgressBar()
        self.operation_progress.setVisible(False)
        self.operation_progress.setFixedWidth(200)
        self.status_bar.addPermanentWidget(self.operation_progress)
    
    def connect_signals(self):
        """Connect signals"""
        # Tab change
        self.central_widget.currentChanged.connect(self.on_tab_changed)
    
    def setup_scanner(self):
        """Setup photo scanner"""
        self.photo_scanner = PhotoScanner(self.config)
        self.photo_scanner.photo_found.connect(self.on_photo_found)
        self.photo_scanner.progress_updated.connect(self.on_scan_progress)
        self.photo_scanner.scanning_started.connect(self.on_scanning_started)
        self.photo_scanner.scanning_finished.connect(self.on_scanning_finished)
        self.photo_scanner.error_occurred.connect(self.on_scan_error)
    
    def handle_startup(self):
        """Handle application startup"""
        try:
            photo_path = self.config.get_photo_path()
            
            if not photo_path:
                # First run - show setup dialog
                self.show_first_run_dialog()
            elif self.config.is_auto_scan_enabled():
                # Auto scan enabled
                self.start_scanning()
            else:
                # Load any existing data or show empty state
                self.update_status("就绪 - 点击 '扫描照片' 开始")
        except Exception as e:
            print(f"Error during startup: {e}")
            self.update_status("启动时出现错误，请检查设置")
    
    def show_first_run_dialog(self):
        """Show first run setup dialog"""
        dialog = FirstRunDialog(self.config, self)
        if dialog.exec_() == dialog.Accepted:
            photo_path = self.config.get_photo_path()
            if photo_path:
                self.start_scanning()
            else:
                self.update_status("Ready - Configure photo path in Settings")
        else:
            self.update_status("就绪 - 在设置中配置照片路径")
    
    def start_scanning(self):
        """Start photo scanning"""
        photo_path = self.config.get_photo_path()
        
        if not photo_path:
            QMessageBox.information(
                self, "未设置照片路径",
                "请先在设置中配置照片目录。"
            )
            self.show_settings()
            return
        
        if not os.path.exists(photo_path):
            QMessageBox.warning(
                self, "路径无效",
                f"配置的照片目录不存在：\n{photo_path}\n\n"
                "请在设置中更新路径。"
            )
            self.show_settings()
            return
        
        # Clear existing data
        self.photo_database.clear()
        
        # Show progress
        self.show_scanning_progress()
        
        # Start scanning
        self.photo_scanner.scan_photos(photo_path)
        
        # Update UI
        self.scan_button.setEnabled(False)
        self.scan_action.setEnabled(False)
        self.update_status("正在扫描照片...")
    
    def cancel_scanning(self):
        """Cancel photo scanning"""
        if self.photo_scanner and self.photo_scanner.isRunning():
            self.photo_scanner.stop_scanning()
            self.update_status("扫描已取消")
            self.hide_scanning_progress()
    
    def show_scanning_progress(self):
        """Show scanning progress"""
        # Add progress tab if not already present
        if self.central_widget.indexOf(self.progress_widget) == -1:
            self.central_widget.addTab(self.progress_widget, "正在扫描...")
        
        self.central_widget.setCurrentWidget(self.progress_widget)
        self.progress_widget.update_progress(0, 100, "初始化扫描...")
    
    def hide_scanning_progress(self):
        """Hide scanning progress"""
        index = self.central_widget.indexOf(self.progress_widget)
        if index != -1:
            self.central_widget.removeTab(index)
        
        # Switch to gallery tab
        self.central_widget.setCurrentIndex(0)
        
        # Re-enable controls
        self.scan_button.setEnabled(True)
        self.scan_action.setEnabled(True)
    
    def on_photo_found(self, photo_info: PhotoInfo):
        """Handle photo found during scanning"""
        self.photo_database.add_photo(photo_info)
    
    def on_scan_progress(self, current: int, total: int):
        """Handle scan progress update"""
        self.progress_widget.update_progress(current, total, "正在扫描照片...")
        
        # Update operation progress bar
        if total > 0:
            self.operation_progress.setVisible(True)
            self.operation_progress.setValue(int((current / total) * 100))
    
    def on_scanning_started(self, folder_path: str):
        """Handle scanning started"""
        self.update_status(f"正在扫描： {folder_path}")
    
    def on_scanning_finished(self, photo_count: int):
        """Handle scanning completion"""
        self.hide_scanning_progress()
        self.operation_progress.setVisible(False)
        
        # Update galleries with photos
        photos = self.photo_database.get_all_photos()
        self.gallery_tab.set_photos(photos)
        self.folder_tab.set_photos(photos)
        
        # Update status
        self.update_photo_count(photo_count)
        if photo_count > 0:
            self.update_status(f"扫描完成 - 找到 {photo_count:,} 张照片")
        else:
            self.update_status("扫描完成 - 未找到照片")
    
    def on_scan_error(self, error_msg: str, file_path: str):
        """Handle scan error"""
        # Log error (in a real app, you'd use proper logging)
        print(f"Scan error: {error_msg} - {file_path}")
        
        # If it's a critical error, stop scanning
        if "路径不存在" in error_msg:
            self.hide_scanning_progress()
            QMessageBox.critical(self, "扫描错误", error_msg)
    
    def on_photo_clicked(self, photo_info: PhotoInfo):
        """Handle photo click"""
        # Could implement photo selection logic here
        pass
    
    def on_photo_right_clicked(self, photo_info: PhotoInfo, position):
        """Handle photo right click"""
        menu = PhotoOperations.create_context_menu(photo_info, self)
        menu.exec_(position)
    
    def on_photo_double_clicked(self, photo_info: PhotoInfo):
        """Handle photo double click"""
        PhotoOperations.open_photo_with_default_viewer(photo_info)
    
    def on_tab_changed(self, index: int):
        """Handle tab change"""
        # Update status based on current tab
        if index == 0:  # Gallery tab
            photo_count = self.photo_database.get_photo_count()
            self.update_photo_count(photo_count)
        elif index == 1:  # Folder tab
            # Could show folder-specific status
            pass
    
    def show_settings(self):
        """Show settings window"""
        settings_window = SettingsWindow(self.config, self)
        settings_window.settings_applied.connect(self.on_settings_applied)
        settings_window.photo_path_changed.connect(self.on_photo_path_changed)
        settings_window.exec_()
    
    def on_settings_applied(self):
        """Handle settings changes"""
        # Apply theme changes
        self.apply_current_theme()
        
        # Update thumbnail sizes
        thumbnail_size = self.config.get_thumbnail_size()
        self.gallery_tab.set_thumbnail_size(thumbnail_size)
        self.folder_tab.set_thumbnail_size(thumbnail_size)
    
    def on_photo_path_changed(self, new_path: str):
        """Handle photo path change"""
        if new_path and os.path.exists(new_path):
            # Ask if user wants to scan now
            reply = QMessageBox.question(
                self, "Photo Path Changed",
                "Photo directory has been changed. Would you like to scan for photos now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.start_scanning()
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        current_theme = self.config.get_theme()
        new_theme = 'light' if current_theme == 'dark' else 'dark'
        self.config.set_theme(new_theme)
        self.apply_current_theme()
    
    def apply_current_theme(self):
        """Apply current theme to application"""
        theme = self.config.get_theme()
        app = QApplication.instance()
        apply_theme(app, theme)
    
    def refresh_view(self):
        """Refresh the current view"""
        current_widget = self.central_widget.currentWidget()
        if current_widget == self.gallery_tab:
            photos = self.photo_database.get_all_photos()
            self.gallery_tab.set_photos(photos)
        elif current_widget == self.folder_tab:
            photos = self.photo_database.get_all_photos()
            self.folder_tab.set_photos(photos)
    
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.setText(message)
    
    def update_photo_count(self, count: int):
        """Update photo count display"""
        if count == 1:
            self.photo_count_label.setText("1 张照片")
        else:
            self.photo_count_label.setText(f"{count:,} 张照片")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "关于现代照片查看器",
            """<h3>现代照片查看器</h3>
            <p>版本 1.0.0</p>
            <p>一款高性能的照片和视频查看器，专为管理
            大量照片集合而设计，具有现代、美观的界面。</p>
            <p>使用 PyQt5 和现代设计原则构建。</p>
            """
        )
    
    def restore_window_state(self):
        """Restore window geometry and state"""
        geometry = self.config.get_window_geometry()
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self.config.get_window_state()
        if state:
            self.restoreState(state)
    
    def closeEvent(self, a0):
        """Handle window close event"""
        # Save window state
        self.config.set_window_geometry(self.saveGeometry())
        self.config.set_window_state(self.saveState())
        
        # Stop any running operations
        if self.photo_scanner and self.photo_scanner.isRunning():
            self.photo_scanner.stop_scanning()
            self.photo_scanner.wait()
        
        a0.accept()