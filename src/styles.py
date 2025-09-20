#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern UI Styling
Beautiful, modern styles for the photo viewer application
Designed with young users' aesthetic preferences in mind
"""

def get_dark_theme_style():
    """Get dark theme stylesheet - modern and sleek"""
    return """
    QMainWindow {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    
    QWidget {
        background-color: #1e1e1e;
        color: #ffffff;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    /* Menu Bar */
    QMenuBar {
        background-color: #2d2d2d;
        color: #ffffff;
        border: none;
        padding: 4px;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 8px 12px;
        border-radius: 4px;
        margin: 2px;
    }
    
    QMenuBar::item:selected {
        background-color: #404040;
    }
    
    QMenuBar::item:pressed {
        background-color: #505050;
    }
    
    QMenu {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #404040;
        border-radius: 6px;
        padding: 4px;
    }
    
    QMenu::item {
        padding: 8px 20px;
        border-radius: 4px;
        margin: 1px;
    }
    
    QMenu::item:selected {
        background-color: #404040;
    }
    
    /* Tool Bar */
    QToolBar {
        background-color: #2d2d2d;
        border: none;
        spacing: 6px;
        padding: 8px;
    }
    
    QToolButton {
        background-color: transparent;
        border: none;
        border-radius: 6px;
        padding: 8px 12px;
        color: #ffffff;
        font-weight: 500;
    }
    
    QToolButton:hover {
        background-color: #404040;
    }
    
    QToolButton:pressed {
        background-color: #505050;
    }
    
    QToolButton:checked {
        background-color: #0d7377;
    }
    
    /* Buttons */
    QPushButton {
        background-color: #0d7377;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        font-size: 14px;
    }
    
    QPushButton:hover {
        background-color: #14a085;
    }
    
    QPushButton:pressed {
        background-color: #0a5d61;
    }
    
    QPushButton:disabled {
        background-color: #404040;
        color: #808080;
    }
    
    /* Secondary Button */
    QPushButton[buttonStyle="secondary"] {
        background-color: #404040;
        color: #ffffff;
    }
    
    QPushButton[buttonStyle="secondary"]:hover {
        background-color: #505050;
    }
    
    /* Line Edit */
    QLineEdit {
        background-color: #2d2d2d;
        border: 2px solid #404040;
        border-radius: 8px;
        padding: 8px 12px;
        color: #ffffff;
        font-size: 14px;
    }
    
    QLineEdit:focus {
        border-color: #0d7377;
    }
    
    /* Labels */
    QLabel {
        color: #ffffff;
        font-size: 14px;
    }
    
    QLabel[labelStyle="heading"] {
        font-size: 18px;
        font-weight: bold;
        color: #0d7377;
    }
    
    QLabel[labelStyle="subheading"] {
        font-size: 16px;
        font-weight: 600;
        color: #ffffff;
    }
    
    QLabel[labelStyle="caption"] {
        font-size: 12px;
        color: #b0b0b0;
    }
    
    /* List Widget */
    QListWidget {
        background-color: #1e1e1e;
        border: 1px solid #404040;
        border-radius: 8px;
        padding: 4px;
        outline: none;
    }
    
    QListWidget::item {
        border-radius: 6px;
        padding: 8px;
        margin: 2px;
    }
    
    QListWidget::item:selected {
        background-color: #0d7377;
        color: #ffffff;
    }
    
    QListWidget::item:hover {
        background-color: #2d2d2d;
    }
    
    /* Tree Widget */
    QTreeWidget {
        background-color: #1e1e1e;
        border: 1px solid #404040;
        border-radius: 8px;
        outline: none;
        alternate-background-color: #252525;
    }
    
    QTreeWidget::item {
        padding: 6px;
        border-radius: 4px;
        margin: 1px;
    }
    
    QTreeWidget::item:selected {
        background-color: #0d7377;
    }
    
    QTreeWidget::item:hover {
        background-color: #2d2d2d;
    }
    
    /* Custom Header Frame */
    QFrame[headerFrame="true"] {
        background-color: #252525;
        border-bottom: 1px solid #404040;
    }
    
    /* Side Panel */
    QFrame[sidePanel="true"] {
        background-color: #252525;
        border-radius: 8px;
    }
    
    /* Main Panel */
    QFrame[mainPanel="true"] {
        background-color: #1e1e1e;
        border-radius: 8px;
    }
    
    /* Breadcrumb */
    QLabel[labelStyle="breadcrumb"] {
        font-size: 12px;
        color: #0d7377;
        background-color: #2d2d2d;
        padding: 4px 8px;
        border-radius: 4px;
    }
    
    QTreeWidget::branch {
        background-color: transparent;
    }
    
    QTreeWidget::branch:hover {
        background-color: #2d2d2d;
    }
    
    /* Scroll Bar */
    QScrollBar:vertical {
        background-color: #2d2d2d;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #505050;
        border-radius: 6px;
        min-height: 20px;
        margin: 2px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #606060;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
    
    QScrollBar:horizontal {
        background-color: #2d2d2d;
        height: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #505050;
        border-radius: 6px;
        min-width: 20px;
        margin: 2px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #606060;
    }
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        border: none;
        background: none;
    }
    
    /* Splitter */
    QSplitter::handle {
        background-color: #404040;
    }
    
    QSplitter::handle:horizontal {
        width: 2px;
    }
    
    QSplitter::handle:vertical {
        height: 2px;
    }
    
    /* Status Bar */
    QStatusBar {
        background-color: #2d2d2d;
        color: #b0b0b0;
        border-top: 1px solid #404040;
        padding: 4px;
    }
    
    /* Tab Widget */
    QTabWidget::pane {
        background-color: #1e1e1e;
        border: 1px solid #404040;
        border-radius: 8px;
    }
    
    QTabBar::tab {
        background-color: #2d2d2d;
        color: #b0b0b0;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }
    
    QTabBar::tab:selected {
        background-color: #0d7377;
        color: #ffffff;
    }
    
    QTabBar::tab:hover {
        background-color: #404040;
        color: #ffffff;
    }
    
    /* Group Box */
    QGroupBox {
        font-weight: 600;
        font-size: 14px;
        color: #0d7377;
        border: 2px solid #404040;
        border-radius: 8px;
        margin-top: 1ex;
        padding-top: 10px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 10px 0 10px;
        background-color: #1e1e1e;
    }
    
    /* Combo Box */
    QComboBox {
        background-color: #2d2d2d;
        border: 2px solid #404040;
        border-radius: 8px;
        padding: 8px 12px;
        color: #ffffff;
        font-size: 14px;
    }
    
    QComboBox:focus {
        border-color: #0d7377;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #b0b0b0;
    }
    
    QComboBox QAbstractItemView {
        background-color: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 6px;
        selection-background-color: #0d7377;
    }
    
    /* Slider */
    QSlider::groove:horizontal {
        border: none;
        height: 6px;
        background-color: #404040;
        border-radius: 3px;
    }
    
    QSlider::handle:horizontal {
        background-color: #0d7377;
        border: none;
        width: 18px;
        height: 18px;
        border-radius: 9px;
        margin: -6px 0;
    }
    
    QSlider::handle:horizontal:hover {
        background-color: #14a085;
    }
    
    QSlider::sub-page:horizontal {
        background-color: #0d7377;
        border-radius: 3px;
    }
    
    /* Dialog */
    QDialog {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    
    /* Progress Bar */
    QProgressBar {
        background-color: #2d2d2d;
        border: none;
        border-radius: 6px;
        text-align: center;
        font-weight: 600;
    }
    
    QProgressBar::chunk {
        background-color: #0d7377;
        border-radius: 6px;
    }
    """

def get_light_theme_style():
    """Get light theme stylesheet - clean and modern"""
    return """
    QMainWindow {
        background-color: #ffffff;
        color: #333333;
    }
    
    QWidget {
        background-color: #ffffff;
        color: #333333;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    /* Menu Bar */
    QMenuBar {
        background-color: #f5f5f5;
        color: #333333;
        border: none;
        padding: 4px;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 8px 12px;
        border-radius: 4px;
        margin: 2px;
    }
    
    QMenuBar::item:selected {
        background-color: #e0e0e0;
    }
    
    QMenuBar::item:pressed {
        background-color: #d0d0d0;
    }
    
    QMenu {
        background-color: #ffffff;
        color: #333333;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 4px;
    }
    
    QMenu::item {
        padding: 8px 20px;
        border-radius: 4px;
        margin: 1px;
    }
    
    QMenu::item:selected {
        background-color: #0d7377;
        color: #ffffff;
    }
    
    /* Tool Bar */
    QToolBar {
        background-color: #f5f5f5;
        border: none;
        spacing: 6px;
        padding: 8px;
    }
    
    QToolButton {
        background-color: transparent;
        border: none;
        border-radius: 6px;
        padding: 8px 12px;
        color: #333333;
        font-weight: 500;
    }
    
    QToolButton:hover {
        background-color: #e0e0e0;
    }
    
    QToolButton:pressed {
        background-color: #d0d0d0;
    }
    
    QToolButton:checked {
        background-color: #0d7377;
        color: #ffffff;
    }
    
    /* Buttons */
    QPushButton {
        background-color: #0d7377;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        font-size: 14px;
    }
    
    QPushButton:hover {
        background-color: #14a085;
    }
    
    QPushButton:pressed {
        background-color: #0a5d61;
    }
    
    QPushButton:disabled {
        background-color: #e0e0e0;
        color: #808080;
    }
    
    /* Secondary Button */
    QPushButton[buttonStyle="secondary"] {
        background-color: #e0e0e0;
        color: #333333;
    }
    
    QPushButton[buttonStyle="secondary"]:hover {
        background-color: #d0d0d0;
    }
    
    /* Line Edit */
    QLineEdit {
        background-color: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 8px 12px;
        color: #333333;
        font-size: 14px;
    }
    
    QLineEdit:focus {
        border-color: #0d7377;
    }
    
    /* Labels */
    QLabel {
        color: #333333;
        font-size: 14px;
    }
    
    QLabel[labelStyle="heading"] {
        font-size: 18px;
        font-weight: bold;
        color: #0d7377;
    }
    
    QLabel[labelStyle="subheading"] {
        font-size: 16px;
        font-weight: 600;
        color: #333333;
    }
    
    QLabel[labelStyle="caption"] {
        font-size: 12px;
        color: #808080;
    }
    
    /* List Widget */
    QListWidget {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 4px;
        outline: none;
    }
    
    QListWidget::item {
        border-radius: 6px;
        padding: 8px;
        margin: 2px;
    }
    
    QListWidget::item:selected {
        background-color: #0d7377;
        color: #ffffff;
    }
    
    QListWidget::item:hover {
        background-color: #f0f0f0;
    }
    
    /* Tree Widget */
    QTreeWidget {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        outline: none;
        alternate-background-color: #f8f8f8;
    }
    
    QTreeWidget::item {
        padding: 6px;
        border-radius: 4px;
        margin: 1px;
    }
    
    QTreeWidget::item:selected {
        background-color: #0d7377;
        color: #ffffff;
    }
    
    QTreeWidget::item:hover {
        background-color: #f0f0f0;
    }
    
    /* Custom Header Frame */
    QFrame[headerFrame="true"] {
        background-color: #f0f0f0;
        border-bottom: 1px solid #e0e0e0;
    }
    
    /* Side Panel */
    QFrame[sidePanel="true"] {
        background-color: #f8f8f8;
        border-radius: 8px;
    }
    
    /* Main Panel */
    QFrame[mainPanel="true"] {
        background-color: #ffffff;
        border-radius: 8px;
    }
    
    /* Breadcrumb */
    QLabel[labelStyle="breadcrumb"] {
        font-size: 12px;
        color: #0d7377;
        background-color: #f0f0f0;
        padding: 4px 8px;
        border-radius: 4px;
    }
    
    /* Scroll Bar */
    QScrollBar:vertical {
        background-color: #f5f5f5;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #c0c0c0;
        border-radius: 6px;
        min-height: 20px;
        margin: 2px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #a0a0a0;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
    
    QScrollBar:horizontal {
        background-color: #f5f5f5;
        height: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #c0c0c0;
        border-radius: 6px;
        min-width: 20px;
        margin: 2px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #a0a0a0;
    }
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        border: none;
        background: none;
    }
    
    /* Status Bar */
    QStatusBar {
        background-color: #f5f5f5;
        color: #808080;
        border-top: 1px solid #e0e0e0;
        padding: 4px;
    }
    """

def apply_theme(app, theme='dark'):
    """Apply theme to application"""
    if theme == 'dark':
        app.setStyleSheet(get_dark_theme_style())
    else:
        app.setStyleSheet(get_light_theme_style())