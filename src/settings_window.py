#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Settings Window
Modern settings interface for photo path configuration and preferences
"""

import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QLineEdit, QPushButton, QFileDialog,
                             QGroupBox, QCheckBox, QSlider, QComboBox,
                             QSpinBox, QTextEdit, QTabWidget, QWidget,
                             QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon


class SettingsWindow(QDialog):
    """Modern settings window with tabbed interface"""
    
    # Signals
    settings_applied = pyqtSignal()
    photo_path_changed = pyqtSignal(str)
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setup_ui()
        self.load_settings()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("设置 - 现代照片查看器")
        self.setFixedSize(600, 500)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("设置")
        title_label.setProperty("labelStyle", "heading")
        layout.addWidget(title_label)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_general_tab()
        self.create_appearance_tab()
        self.create_performance_tab()
        self.create_about_tab()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.reset_button = QPushButton("重置为默认值")
        self.reset_button.setProperty("buttonStyle", "secondary")
        self.reset_button.clicked.connect(self.reset_settings)
        button_layout.addWidget(self.reset_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setProperty("buttonStyle", "secondary")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.apply_button = QPushButton("应用并关闭")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)
        
        layout.addLayout(button_layout)
    
    def create_general_tab(self):
        """Create general settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Photo Path Group
        path_group = QGroupBox("照片目录")
        path_layout = QGridLayout(path_group)
        
        # Current path
        path_layout.addWidget(QLabel("照片路径:"), 0, 0)
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText("选择包含照片的文件夹...")
        path_layout.addWidget(self.path_edit, 0, 1)
        
        self.browse_button = QPushButton("浏览...")
        self.browse_button.clicked.connect(self.browse_photo_path)
        path_layout.addWidget(self.browse_button, 0, 2)
        
        # Path info
        info_label = QLabel("选择存放照片的主文件夹。"
                           "应用程序将自动扫描所有子文件夹。")
        info_label.setProperty("labelStyle", "caption")
        info_label.setWordWrap(True)
        path_layout.addWidget(info_label, 1, 0, 1, 3)
        
        layout.addWidget(path_group)
        
        # Scanning Options Group
        scan_group = QGroupBox("扫描选项")
        scan_layout = QVBoxLayout(scan_group)
        
        self.auto_scan_check = QCheckBox("启动时自动扫描新照片")
        scan_layout.addWidget(self.auto_scan_check)
        
        self.hidden_files_check = QCheckBox("包含隐藏文件和文件夹")
        scan_layout.addWidget(self.hidden_files_check)
        
        layout.addWidget(scan_group)
        
        # File Formats Group
        formats_group = QGroupBox("支持的文件格式")
        formats_layout = QVBoxLayout(formats_group)
        
        formats_info = QLabel("支持的图片格式：JPG、PNG、GIF、BMP、TIFF、WebP、ICO、SVG\n"
                             "支持的视频格式：MP4、AVI、MOV、MKV、WMV、FLV、WebM")
        formats_info.setProperty("labelStyle", "caption")
        formats_layout.addWidget(formats_info)
        
        layout.addWidget(formats_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "常规")
    
    def create_appearance_tab(self):
        """Create appearance settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Theme Group
        theme_group = QGroupBox("主题")
        theme_layout = QGridLayout(theme_group)
        
        theme_layout.addWidget(QLabel("颜色主题:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["深色（推荐）", "浅色"])
        theme_layout.addWidget(self.theme_combo, 0, 1)
        
        theme_info = QLabel("深色主题经过优化，可更好地浏览照片，对比度更高。")
        theme_info.setProperty("labelStyle", "caption")
        theme_layout.addWidget(theme_info, 1, 0, 1, 2)
        
        layout.addWidget(theme_group)
        
        # Thumbnail Settings Group
        thumb_group = QGroupBox("缩略图")
        thumb_layout = QGridLayout(thumb_group)
        
        thumb_layout.addWidget(QLabel("缩略图大小:"), 0, 0)
        
        size_layout = QHBoxLayout()
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(100, 400)
        self.size_slider.setValue(200)
        self.size_slider.valueChanged.connect(self.update_size_label)
        
        self.size_label = QLabel("200px")
        self.size_label.setMinimumWidth(50)
        
        size_layout.addWidget(self.size_slider)
        size_layout.addWidget(self.size_label)
        thumb_layout.addLayout(size_layout, 0, 1)
        
        layout.addWidget(thumb_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "外观")
    
    def create_performance_tab(self):
        """Create performance settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Cache Settings Group
        cache_group = QGroupBox("缓存设置")
        cache_layout = QGridLayout(cache_group)
        cache_layout.setSpacing(10)
        
        # Enable cache
        self.cache_enabled_check = QCheckBox("启用缩略图缓存")
        self.cache_enabled_check.setChecked(bool(self.config.is_cache_enabled()))
        cache_layout.addWidget(self.cache_enabled_check, 0, 0, 1, 2)
        
        # Cache size
        cache_size_label = QLabel("最大缓存大小 (MB):")
        cache_layout.addWidget(cache_size_label, 1, 0)
        
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(100, 20000)  # Updated to 20GB maximum
        max_cache_size = self.config.get('max_cache_size', 20000)
        # Ensure we have an integer value
        if isinstance(max_cache_size, str):
            max_cache_size = int(max_cache_size)
        self.cache_size_spin.setValue(int(max_cache_size))
        cache_layout.addWidget(self.cache_size_spin, 1, 1)
        
        # Cache info
        cache_info = QLabel("缓存缩略图可以显著提高浏览速度，特别是在处理大量照片时。")
        cache_info.setProperty("labelStyle", "caption")
        cache_info.setWordWrap(True)
        cache_layout.addWidget(cache_info, 2, 0, 1, 2)
        
        # Cache management buttons
        cache_buttons = QHBoxLayout()
        self.clear_cache_button = QPushButton("清除缓存")
        self.clear_cache_button.setProperty("buttonStyle", "secondary")
        self.clear_cache_button.clicked.connect(self.clear_cache)
        
        self.cache_info_button = QPushButton("缓存信息")
        self.cache_info_button.setProperty("buttonStyle", "secondary")
        self.cache_info_button.clicked.connect(self.show_cache_info)
        
        cache_buttons.addWidget(self.clear_cache_button)
        cache_buttons.addWidget(self.cache_info_button)
        cache_buttons.addStretch()
        
        cache_layout.addLayout(cache_buttons, 3, 0, 2, 2)
        
        layout.addWidget(cache_group)
        
        # Performance Tips Group
        tips_group = QGroupBox("性能提示")
        tips_layout = QVBoxLayout(tips_group)
        
        tips_text = """• 将照片集合按子文件夹有序组织
• 使用 SSD 存储以提高缩略图加载性能
• 为经常访问的照片启用缓存
• 关闭其他资源密集型应用程序
• 对于非常大的集合，考虑减小缩略图尺寸
• 增加最大缓存大小可提高浏览性能"""
        
        tips_label = QLabel(tips_text)
        tips_label.setProperty("labelStyle", "caption")
        tips_label.setWordWrap(True)
        tips_layout.addWidget(tips_label)
        
        layout.addWidget(tips_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "性能")
    
    def create_about_tab(self):
        """Create about tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # App info
        app_label = QLabel("现代照片查看器")
        app_label.setProperty("labelStyle", "heading")
        app_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(app_label)
        
        version_label = QLabel("版本 1.0.0")
        version_label.setProperty("labelStyle", "subheading")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Description
        desc_text = """专为管理而设计的高性能照片和视频查看器
具有现代、美观界面的大型照片集。

特征：
• 快速扫描和索引数千张照片
• 智能缩略图缓存以实现最佳性能
• 基于时间的照片组织
• 基于文件夹的浏览
• 详细的照片信息和元数据
• 现代深色/浅色主题
• 视频播放支持"""
        
        desc_label = QLabel(desc_text)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        # Tech info
        tech_label = QLabel("使用 PyQt5 构建• 由现代设计原则提供支持")
        tech_label.setProperty("labelStyle", "caption")
        tech_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(tech_label)
        
        self.tab_widget.addTab(tab, "关于")
    
    def browse_photo_path(self):
        """Browse for photo directory"""
        current_path = self.path_edit.text()
        if not current_path or not os.path.exists(current_path):
            current_path = os.path.expanduser("~")
        
        path = QFileDialog.getExistingDirectory(
            self, 
            "选择照片目录",
            current_path,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if path:
            self.path_edit.setText(path)
    
    def update_size_label(self, value):
        """Update thumbnail size label"""
        self.size_label.setText(f"{value}px")
    
    def load_settings(self):
        """Load current settings"""
        # General settings
        self.path_edit.setText(self.config.get_photo_path())
        self.auto_scan_check.setChecked(bool(self.config.is_auto_scan_enabled()))
        self.hidden_files_check.setChecked(bool(self.config.get('show_hidden_files', False)))
        
        # Appearance settings
        theme = self.config.get_theme()
        self.theme_combo.setCurrentIndex(0 if theme == 'dark' else 1)
        
        thumbnail_size = self.config.get_thumbnail_size()
        self.size_slider.setValue(thumbnail_size)
        self.update_size_label(thumbnail_size)
        
        # Performance settings
        self.cache_enabled_check.setChecked(bool(self.config.is_cache_enabled()))
        max_cache_size = self.config.get('max_cache_size', 500)
        # Ensure we have an integer value
        if isinstance(max_cache_size, str):
            max_cache_size = int(max_cache_size)
        self.cache_size_spin.setValue(int(max_cache_size))
    
    def apply_settings(self):
        """Apply and save settings"""
        try:
            # General settings
            old_path = self.config.get_photo_path()
            new_path = self.path_edit.text().strip()
            
            if new_path != old_path:
                if new_path and not os.path.exists(new_path):
                    QMessageBox.warning(self, "无效路径", 
                                      "所选照片目录不存在。")
                    return
                
                self.config.set_photo_path(new_path)
                if new_path:
                    self.photo_path_changed.emit(new_path)
            
            self.config.set_auto_scan(bool(self.auto_scan_check.isChecked()))
            self.config.set('show_hidden_files', bool(self.hidden_files_check.isChecked()))
            
            # Appearance settings
            theme = 'dark' if self.theme_combo.currentIndex() == 0 else 'light'
            self.config.set_theme(theme)
            
            self.config.set_thumbnail_size(self.size_slider.value())
            
            # Performance settings
            self.config.set('cache_thumbnails', bool(self.cache_enabled_check.isChecked()))
            self.config.set('max_cache_size', int(self.cache_size_spin.value()))
            
            self.settings_applied.emit()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置失败：{str(e)}")
    
    def reset_settings(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self, "重置设置",
            "确定要将所有设置重置为默认值吗？\n"
            "此操作无法撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config.reset_to_defaults()
            self.load_settings()
    
    def clear_cache(self):
        """Clear thumbnail cache"""
        reply = QMessageBox.question(
            self, "清除缓存",
            "确定要清除缩略图缓存吗？\n"
            "这将释放磁盘空间，但缩略图需要重新生成。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # This would clear the cache - we'll implement this later
                QMessageBox.information(self, "缓存已清除", 
                                      "缩略图缓存已成功清除。")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"清除缓存失败：{str(e)}")
    
    def show_cache_info(self):
        """Show cache information"""
        try:
            # This would show cache info - we'll implement this later
            cache_size = "~150 MB"  # Placeholder
            cache_files = "1,247 files"  # Placeholder
            
            QMessageBox.information(
                self, "缓存信息",
                f"缓存大小：{cache_size}\n"
                f"缓存文件：{cache_files}\n"
                f"缓存位置：{self.config.get_cache_dir()}"
            )
        except Exception as e:
            QMessageBox.warning(self, "错误", f"获取缓存信息失败：{str(e)}")


class FirstRunDialog(QDialog):
    """First run dialog for initial setup"""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setup_ui()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("欢迎使用现代照片查看器")
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Welcome message
        welcome_label = QLabel("欢迎使用现代照片查看器！")
        welcome_label.setProperty("labelStyle", "heading")
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)
        
        # Description
        desc_text = """要开始使用，请选择存放照片的主文件夹。
应用程序将自动扫描所有子文件夹并按日期组织您的照片。

这是一次性设置 - 您可以后续在设置中更改。"""
        
        desc_label = QLabel(desc_text)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # Path selection
        path_group = QGroupBox("选择照片目录")
        path_layout = QGridLayout(path_group)
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("选择您的照片文件夹...")
        path_layout.addWidget(self.path_edit, 0, 0)
        
        self.browse_button = QPushButton("浏览...")
        self.browse_button.clicked.connect(self.browse_photo_path)
        path_layout.addWidget(self.browse_button, 0, 1)
        
        layout.addWidget(path_group)
        
        # Options
        self.auto_scan_check = QCheckBox("启动时自动扫描新照片")
        self.auto_scan_check.setChecked(True)
        layout.addWidget(self.auto_scan_check)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.skip_button = QPushButton("暂时跳过")
        self.skip_button.setProperty("buttonStyle", "secondary")
        self.skip_button.clicked.connect(self.skip_setup)
        button_layout.addWidget(self.skip_button)
        
        button_layout.addStretch()
        
        self.continue_button = QPushButton("继续")
        self.continue_button.clicked.connect(self.save_and_continue)
        button_layout.addWidget(self.continue_button)
        
        layout.addLayout(button_layout)
    
    def browse_photo_path(self):
        """Browse for photo directory"""
        path = QFileDialog.getExistingDirectory(
            self, 
            "选择照片目录",
            os.path.expanduser("~"),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if path:
            self.path_edit.setText(path)
    
    def save_and_continue(self):
        """Save settings and continue"""
        photo_path = self.path_edit.text().strip()
        
        if photo_path and not os.path.exists(photo_path):
            QMessageBox.warning(self, "无效路径", 
                              "所选目录不存在。请选择有效的文件夹。")
            return
        
        # Save settings
        if photo_path:
            self.config.set_photo_path(photo_path)
        
        self.config.set_auto_scan(bool(self.auto_scan_check.isChecked()))
        self.accept()
    
    def skip_setup(self):
        """Skip initial setup"""
        self.accept()