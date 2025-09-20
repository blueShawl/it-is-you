#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern Photo & Video Viewer
A high-performance photo viewer application built with PyQt5
Designed for handling thousands of photos efficiently with a modern UI
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase

from src.main_window import MainWindow
from src.config import Config


def setup_application():
    """Setup application properties and styles"""
    # Enable high DPI scaling BEFORE creating QApplication
    import sys
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("现代照片查看器")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("照片查看器")
    
    # Set application font
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    return app


def main():
    """Main application entry point"""
    # Create application
    app = setup_application()
    
    # Load configuration
    config = Config()
    
    # Create and show main window
    main_window = MainWindow(config)
    main_window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()