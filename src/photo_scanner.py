#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Scanner and Metadata Extractor
High-performance photo scanning with metadata extraction
Optimized for handling thousands of photos efficiently
"""

import os
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker
from PyQt5.QtGui import QPixmap
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS


@dataclass
class PhotoInfo:
    """Photo information data class"""
    file_path: str
    file_name: str
    file_size: int
    creation_time: datetime
    modification_time: datetime
    width: int
    height: int
    format: str
    folder_path: str
    thumbnail_path: Optional[str] = None
    exif_data: Optional[Dict] = None
    file_hash: Optional[str] = None


class PhotoScanner(QThread):
    """High-performance photo scanner with metadata extraction"""
    
    # Signals
    photo_found = pyqtSignal(PhotoInfo)
    progress_updated = pyqtSignal(int, int)  # current, total
    scanning_started = pyqtSignal(str)  # folder path
    scanning_finished = pyqtSignal(int)  # total photos found
    error_occurred = pyqtSignal(str, str)  # error message, file path
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.mutex = QMutex()
        self.should_stop = False
        self.current_folder = ""
        self.photos_found = 0
        self.total_files = 0
        
    def scan_photos(self, root_path: str):
        """Start scanning photos in given path"""
        if not root_path or not os.path.exists(root_path):
            self.error_occurred.emit("路径不存在或为空", root_path or "")
            return
            
        self.root_path = root_path
        self.should_stop = False
        self.photos_found = 0
        self.start()
    
    def stop_scanning(self):
        """Stop the scanning process"""
        with QMutexLocker(self.mutex):
            self.should_stop = True
    
    def run(self):
        """Main scanning thread execution"""
        try:
            self.scanning_started.emit(self.root_path)
            
            # First pass: count total files
            self.total_files = self._count_files(self.root_path)
            
            # Second pass: process files
            self._scan_directory(self.root_path)
            
            self.scanning_finished.emit(self.photos_found)
            
        except Exception as e:
            self.error_occurred.emit(f"Scanning error: {str(e)}", self.root_path)
    
    def _count_files(self, root_path: str) -> int:
        """Count total files for progress tracking"""
        total = 0
        supported_formats = set(ext.lower() for ext in self.config.get_supported_formats())
        video_formats = set(ext.lower() for ext in self.config.get_video_formats())
        all_formats = supported_formats | video_formats
        
        try:
            for root, dirs, files in os.walk(root_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if self._should_stop():
                        return total
                    
                    _, ext = os.path.splitext(file.lower())
                    if ext in all_formats:
                        total += 1
        except Exception:
            pass
        
        return total
    
    def _scan_directory(self, root_path: str):
        """Recursively scan directory for photos"""
        supported_formats = set(ext.lower() for ext in self.config.get_supported_formats())
        video_formats = set(ext.lower() for ext in self.config.get_video_formats())
        all_formats = supported_formats | video_formats
        
        processed = 0
        
        try:
            for root, dirs, files in os.walk(root_path):
                if self._should_stop():
                    break
                
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                self.current_folder = root
                
                for file in files:
                    if self._should_stop():
                        break
                    
                    processed += 1
                    self.progress_updated.emit(processed, self.total_files)
                    
                    file_path = os.path.join(root, file)
                    _, ext = os.path.splitext(file.lower())
                    
                    if ext in all_formats:
                        try:
                            photo_info = self._extract_photo_info(file_path)
                            if photo_info:
                                self.photo_found.emit(photo_info)
                                self.photos_found += 1
                        except Exception as e:
                            self.error_occurred.emit(f"Error processing {file}: {str(e)}", file_path)
                            
        except Exception as e:
            self.error_occurred.emit(f"Directory scanning error: {str(e)}", root_path)
    
    def _should_stop(self) -> bool:
        """Check if scanning should stop"""
        with QMutexLocker(self.mutex):
            return self.should_stop
    
    def _extract_photo_info(self, file_path: str) -> Optional[PhotoInfo]:
        """Extract comprehensive photo information"""
        try:
            if not os.path.exists(file_path):
                return None
            
            # Basic file info
            stat = os.stat(file_path)
            file_name = os.path.basename(file_path)
            file_size = stat.st_size
            modification_time = datetime.fromtimestamp(stat.st_mtime)
            creation_time = datetime.fromtimestamp(stat.st_ctime)
            folder_path = os.path.dirname(file_path)
            
            # File format
            _, ext = os.path.splitext(file_path.lower())
            format_name = ext[1:].upper() if ext else "UNKNOWN"
            
            # Initialize dimensions
            width, height = 0, 0
            exif_data = None
            
            # Try to get image info and EXIF data
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
                    
                    # Extract EXIF data
                    if hasattr(img, '_getexif') and img._getexif() is not None:
                        exif_dict = {}
                        exif = img._getexif()
                        
                        for tag_id, value in exif.items():
                            tag = TAGS.get(tag_id, tag_id)
                            exif_dict[tag] = value
                        
                        exif_data = exif_dict
                        
                        # Try to get better creation time from EXIF
                        if 'DateTime' in exif_data:
                            try:
                                exif_time = datetime.strptime(exif_data['DateTime'], '%Y:%m:%d %H:%M:%S')
                                creation_time = exif_time
                            except ValueError:
                                pass
                        elif 'DateTimeOriginal' in exif_data:
                            try:
                                exif_time = datetime.strptime(exif_data['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
                                creation_time = exif_time
                            except ValueError:
                                pass
                                
            except Exception:
                # If image processing fails, it might be a video or corrupted file
                # For videos, we'll handle them differently
                pass
            
            # Generate file hash for duplicate detection
            file_hash = self._generate_file_hash(file_path)
            
            return PhotoInfo(
                file_path=file_path,
                file_name=file_name,
                file_size=file_size,
                creation_time=creation_time,
                modification_time=modification_time,
                width=width,
                height=height,
                format=format_name,
                folder_path=folder_path,
                exif_data=exif_data,
                file_hash=file_hash
            )
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to extract info from {file_path}: {str(e)}", file_path)
            return None
    
    def _generate_file_hash(self, file_path: str) -> str:
        """Generate MD5 hash for file duplicate detection"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                # Read in chunks for large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""


class PhotoDatabase:
    """In-memory photo database with fast search capabilities"""
    
    def __init__(self):
        self.photos: List[PhotoInfo] = []
        self.photos_by_folder: Dict[str, List[PhotoInfo]] = {}
        self.photos_by_hash: Dict[str, PhotoInfo] = {}
        self.mutex = QMutex()
    
    def add_photo(self, photo_info: PhotoInfo):
        """Add photo to database"""
        with QMutexLocker(self.mutex):
            self.photos.append(photo_info)
            
            # Index by folder
            folder = photo_info.folder_path
            if folder not in self.photos_by_folder:
                self.photos_by_folder[folder] = []
            self.photos_by_folder[folder].append(photo_info)
            
            # Index by hash for duplicate detection
            if photo_info.file_hash:
                self.photos_by_hash[photo_info.file_hash] = photo_info
    
    def get_all_photos(self) -> List[PhotoInfo]:
        """Get all photos sorted by creation time (newest first)"""
        with QMutexLocker(self.mutex):
            return sorted(self.photos, key=lambda p: p.creation_time, reverse=True)
    
    def get_photos_by_folder(self, folder_path: str) -> List[PhotoInfo]:
        """Get photos in specific folder"""
        with QMutexLocker(self.mutex):
            return self.photos_by_folder.get(folder_path, [])
    
    def get_all_folders(self) -> List[str]:
        """Get all folders containing photos"""
        with QMutexLocker(self.mutex):
            return list(self.photos_by_folder.keys())
    
    def search_photos(self, query: str) -> List[PhotoInfo]:
        """Search photos by filename"""
        with QMutexLocker(self.mutex):
            query_lower = query.lower()
            return [photo for photo in self.photos 
                   if query_lower in photo.file_name.lower()]
    
    def get_photo_count(self) -> int:
        """Get total photo count"""
        with QMutexLocker(self.mutex):
            return len(self.photos)
    
    def clear(self):
        """Clear all photos from database"""
        with QMutexLocker(self.mutex):
            self.photos.clear()
            self.photos_by_folder.clear()
            self.photos_by_hash.clear()
    
    def find_duplicates(self) -> List[List[PhotoInfo]]:
        """Find duplicate photos by hash"""
        with QMutexLocker(self.mutex):
            hash_groups = {}
            
            for photo in self.photos:
                if photo.file_hash:
                    if photo.file_hash not in hash_groups:
                        hash_groups[photo.file_hash] = []
                    hash_groups[photo.file_hash].append(photo)
            
            # Return groups with more than one photo
            return [group for group in hash_groups.values() if len(group) > 1]