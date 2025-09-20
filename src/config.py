#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Manager
Handles application settings with persistence
"""

import os
import json
from PyQt5.QtCore import QSettings, QStandardPaths


class Config:
    """Configuration manager for application settings"""
    
    def __init__(self):
        self.settings = QSettings("PhotoViewer", "ModernPhotoViewer")
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default configuration values with optimized defaults"""
        self.defaults = {
            'photo_path': '',
            'window_geometry': None,
            'window_state': None,
            'thumbnail_size': 180,  # Reduced default size for better performance
            'show_hidden_files': False,
            'supported_formats': [
                '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
                '.webp', '.ico', '.svg'
            ],
            'video_formats': [
                '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm',
                '.m4v', '.3gp', '.ogv'
            ],
            'theme': 'dark',
            'auto_scan': True,
            'cache_thumbnails': True,
            'max_cache_size': 20000,  # Increased to 20GB (20000 MB) as requested
            'max_thumbnails': 200   # Increased maximum number of active thumbnails
        }
    
    def get(self, key, default=None):
        """Get configuration value"""
        if default is None:
            default = self.defaults.get(key)
        return self.settings.value(key, default)
    
    def set(self, key, value):
        """Set configuration value"""
        self.settings.setValue(key, value)
        self.settings.sync()
    
    def get_photo_path(self):
        """Get configured photo path"""
        return self.get('photo_path', '')
    
    def set_photo_path(self, path):
        """Set photo path"""
        self.set('photo_path', path)
    
    def get_supported_formats(self):
        """Get list of supported image formats"""
        formats = self.get('supported_formats')
        if isinstance(formats, str):
            # Handle case where settings stored as string
            return self.defaults['supported_formats']
        return formats or self.defaults['supported_formats']
    
    def get_video_formats(self):
        """Get list of supported video formats"""
        formats = self.get('video_formats')
        if isinstance(formats, str):
            return self.defaults['video_formats']
        return formats or self.defaults['video_formats']
    
    def get_thumbnail_size(self):
        """Get thumbnail size"""
        size = self.get('thumbnail_size', 200)
        try:
            return int(size)
        except (ValueError, TypeError):
            return 200
    
    def set_thumbnail_size(self, size):
        """Set thumbnail size"""
        self.set('thumbnail_size', int(size))
    
    def get_theme(self):
        """Get UI theme"""
        return self.get('theme', 'dark')
    
    def set_theme(self, theme):
        """Set UI theme"""
        self.set('theme', theme)
    
    def get_window_geometry(self):
        """Get saved window geometry"""
        return self.get('window_geometry')
    
    def set_window_geometry(self, geometry):
        """Save window geometry"""
        self.set('window_geometry', geometry)
    
    def get_window_state(self):
        """Get saved window state"""
        return self.get('window_state')
    
    def set_window_state(self, state):
        """Save window state"""
        self.set('window_state', state)
    
    def is_cache_enabled(self):
        """Check if thumbnail caching is enabled"""
        value = self.get('cache_thumbnails', True)
        # Ensure we return a boolean value
        if isinstance(value, str):
            return value.lower() == 'true'
        return bool(value)
    
    def is_auto_scan_enabled(self):
        """Check if auto scan is enabled"""
        value = self.get('auto_scan', True)
        # Ensure we return a boolean value
        if isinstance(value, str):
            return value.lower() == 'true'
        return bool(value)
    
    def set_auto_scan(self, enabled):
        """Set auto scan preference"""
        self.set('auto_scan', enabled)
    
    def get_cache_dir(self):
        """Get cache directory path"""
        cache_dir = QStandardPaths.writableLocation(QStandardPaths.CacheLocation)
        app_cache_dir = os.path.join(cache_dir, "ModernPhotoViewer")
        os.makedirs(app_cache_dir, exist_ok=True)
        return app_cache_dir
    
    def get_max_thumbnails(self):
        """Get maximum number of active thumbnails"""
        max_thumbnails = self.get('max_thumbnails', 200)  # Increased default
        try:
            return int(max_thumbnails)
        except (ValueError, TypeError):
            return 200
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings.clear()
        self.settings.sync()