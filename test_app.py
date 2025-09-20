#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 测试照片查看器的基本功能
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from src.config import Config
from src.main_window import MainWindow

def test_with_sample_photos():
    """使用示例照片测试应用程序"""
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 创建配置并设置示例照片路径
    config = Config()
    sample_path = os.path.abspath("sample_photos")
    
    if os.path.exists(sample_path):
        config.set_photo_path(sample_path)
        print(f"设置照片路径为: {sample_path}")
    else:
        print("示例照片目录不存在，请先运行 create_sample_photos.py")
        return
    
    # 创建主窗口
    main_window = MainWindow(config)
    main_window.show()
    
    # 显示消息
    QMessageBox.information(main_window, "测试模式", 
                          f"应用程序已启动，照片路径已设置为：\n{sample_path}\n\n"
                          "点击工具栏中的'扫描照片'按钮开始测试。")
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_with_sample_photos()