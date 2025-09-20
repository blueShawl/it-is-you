#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thumbnail Generator and Cache Manager
High-performance thumbnail generation with smart caching
Optimized for handling thousands of photos efficiently
"""

import os
import hashlib
from typing import Optional, Tuple
from PyQt5.QtCore import QObject, pyqtSignal, QMutex, QMutexLocker, QSize, QTimer
from PyQt5.QtGui import QPixmap, QImage, QPainter, QBrush, QColor
from PyQt5.QtCore import Qt
from PIL import Image, ImageOps


class ThumbnailGenerator(QObject):
    """High-performance thumbnail generator"""
    
    # Signals
    thumbnail_ready = pyqtSignal(str, QPixmap)  # file_path, thumbnail
    generation_progress = pyqtSignal(int, int)  # current, total
    error_occurred = pyqtSignal(str, str)  # error message, file path
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.mutex = QMutex()
        self.request_queue = []
        self.should_stop = False
        self.cache_dir = config.get_cache_dir()
        self.thumbnail_cache = {}
        self.processing = False
        self.max_batch_size = 20  # Increase batch size for better performance
        self.debug_mode = False  # Disable debug logging for better performance
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Use timer for processing requests with optimized interval
        self.process_timer = QTimer(parent)
        self.process_timer.timeout.connect(self._process_next_batch)
        self.process_timer.setInterval(50)  # Process every 50ms for better responsiveness
    
    def request_thumbnail(self, file_path: str, size: int = None):
        """Request thumbnail generation for a file"""
        if size is None:
            size = self.config.get_thumbnail_size()
        
        with QMutexLocker(self.mutex):
            if file_path not in [req[0] for req in self.request_queue]:
                self.request_queue.append((file_path, size))
        
        # Start processing if not already running
        if not self.process_timer.isActive():
            self.process_timer.start()
    
    def request_thumbnails_batch(self, file_paths: list, size: int = None):
        """Request thumbnails for multiple files"""
        if size is None:
            size = self.config.get_thumbnail_size()
        
        with QMutexLocker(self.mutex):
            for file_path in file_paths:
                if file_path not in [req[0] for req in self.request_queue]:
                    self.request_queue.append((file_path, size))
        
        # Start processing if not already running
        if not self.process_timer.isActive():
            self.process_timer.start()
    
    def stop_generation(self):
        """Stop thumbnail generation"""
        self.process_timer.stop()
        with QMutexLocker(self.mutex):
            self.should_stop = True
            self.request_queue.clear()
    
    def clear_queue(self):
        """Clear the request queue"""
        with QMutexLocker(self.mutex):
            self.request_queue.clear()
    
    def _process_next_batch(self):
        """Process a batch of thumbnail requests"""
        if self.processing:
            return
            
        with QMutexLocker(self.mutex):
            if self.should_stop or not self.request_queue:
                self.process_timer.stop()
                return
                
            # Process a batch of requests at once
            batch_size = min(self.max_batch_size, len(self.request_queue))
            batch = self.request_queue[:batch_size]
            self.request_queue = self.request_queue[batch_size:]
            total_requests = len(self.request_queue)
        
        self.processing = True
        
        try:
            # Process the batch
            for file_path, size in batch:
                try:
                    # Check cache first
                    thumbnail = self._get_cached_thumbnail(file_path, size)
                    
                    if thumbnail is None:
                        # Generate new thumbnail
                        thumbnail = self._generate_thumbnail(file_path, size)
                        
                        if thumbnail and self.config.is_cache_enabled():
                            self._cache_thumbnail(file_path, thumbnail, size)
                    
                    if thumbnail and not thumbnail.isNull():
                        self.thumbnail_ready.emit(file_path, thumbnail)
                    else:
                        if self.debug_mode:
                            print(f"Failed to generate thumbnail for {file_path}")
                        # Generate error placeholder
                        error_thumb = self._create_error_thumbnail(size, "加载失败")
                        self.thumbnail_ready.emit(file_path, error_thumb)
                        
                except Exception as e:
                    if self.debug_mode:
                        print(f"Error processing thumbnail: {e}")
                    self.error_occurred.emit(f"Thumbnail generation failed: {str(e)}", file_path)
            
            # Emit progress
            self.generation_progress.emit(total_requests, total_requests + batch_size)
            
        finally:
            self.processing = False
            
            # Continue processing if there are more requests
            with QMutexLocker(self.mutex):
                if self.request_queue and not self.should_stop:
                    # Continue processing
                    pass
                else:
                    self.process_timer.stop()
    
    def _generate_thumbnail(self, file_path: str, size: int) -> Optional[QPixmap]:
        """Generate thumbnail for image file"""
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return None
            
            # Get file extension
            _, ext = os.path.splitext(file_path.lower())
            
            # Handle different file types
            if ext in self.config.get_supported_formats():
                return self._generate_image_thumbnail(file_path, size)
            elif ext in self.config.get_video_formats():
                return self._generate_video_thumbnail(file_path, size)
            
            return None
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to generate thumbnail: {str(e)}", file_path)
            return None
    
    def _generate_image_thumbnail(self, file_path: str, size: int) -> Optional[QPixmap]:
        """Generate thumbnail for image files with optimized approach"""
        try:
            # Check if file exists and is readable
            if not os.path.exists(file_path) or not os.access(file_path, os.R_OK):
                if self.debug_mode:
                    print(f"File not found or not readable: {file_path}")
                return None
            
            # Direct QPixmap loading - simplest and fastest approach for standard formats
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Scale to thumbnail size with optimized transformation
                scaled = pixmap.scaled(
                    size, size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                # Add rounded corners
                return self._add_rounded_corners(scaled, 8)
            
            # If QPixmap failed, try PIL as a fallback with optimizations
            try:
                with Image.open(file_path) as image:
                    # Handle EXIF orientation
                    try:
                        image = ImageOps.exif_transpose(image)
                    except Exception as e:
                        if self.debug_mode:
                            print(f"EXIF transpose error: {e}")
                    
                    # Convert to RGB if necessary (only when needed)
                    if image.mode not in ('RGB', 'RGBA'):
                        image = image.convert('RGB')
                    
                    # Calculate thumbnail size maintaining aspect ratio
                    img_width, img_height = image.size
                    aspect_ratio = img_width / img_height
                    
                    if aspect_ratio > 1:
                        # Landscape
                        thumb_width = size
                        thumb_height = int(size / aspect_ratio)
                    else:
                        # Portrait
                        thumb_width = int(size * aspect_ratio)
                        thumb_height = size
                    
                    # Use faster resampling for better performance
                    # LANCZOS is high quality but slower, BILINEAR is faster
                    thumbnail = image.resize((thumb_width, thumb_height), Image.Resampling.BILINEAR)
                    
                    # Convert PIL image to QPixmap more efficiently
                    if thumbnail.mode == 'RGB':
                        # Use more efficient conversion
                        qimage = QImage(thumbnail.tobytes(), thumb_width, thumb_height, QImage.Format.Format_RGB888)
                    elif thumbnail.mode == 'RGBA':
                        qimage = QImage(thumbnail.tobytes(), thumb_width, thumb_height, QImage.Format.Format_RGBA8888)
                    else:
                        # Fallback conversion
                        thumbnail = thumbnail.convert('RGB')
                        qimage = QImage(thumbnail.tobytes(), thumb_width, thumb_height, QImage.Format.Format_RGB888)
                    
                    # Create pixmap
                    if qimage.isNull():
                        if self.debug_mode:
                            print(f"Created null QImage for {file_path}")
                        return None
                        
                    pixmap = QPixmap.fromImage(qimage)
                    if pixmap.isNull():
                        if self.debug_mode:
                            print(f"Created null QPixmap for {file_path}")
                        return None
                        
                    # Return pixmap with rounded corners
                    return self._add_rounded_corners(pixmap, 8)
            except Exception as pil_error:
                if self.debug_mode:
                    print(f"PIL processing error for {file_path}: {pil_error}")
                return None
                
        except Exception as e:
            if self.debug_mode:
                print(f"Thumbnail generation error for {file_path}: {e}")
            # Create error placeholder
            return self._create_error_thumbnail(size, f"Error: {str(e)[:20]}...")
    
    def _generate_video_thumbnail(self, file_path: str, size: int) -> Optional[QPixmap]:
        """Generate thumbnail for video files (placeholder for now)"""
        try:
            # For now, create a video icon placeholder
            # In a full implementation, you'd use ffmpeg or similar to extract a frame
            return self._create_video_placeholder(size, os.path.basename(file_path))
            
        except Exception as e:
            return self._create_error_thumbnail(size, "Video Error")
    
    def _create_video_placeholder(self, size: int, filename: str) -> QPixmap:
        """Create a placeholder thumbnail for video files"""
        try:
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(45, 45, 45))
            
            painter = QPainter(pixmap)
            if not painter.isActive():
                return pixmap
                
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw video icon (triangle play button)
            painter.setBrush(QBrush(QColor(13, 115, 119)))
            painter.setPen(Qt.NoPen)
            
            # Draw play triangle
            triangle_size = size // 3
            center_x, center_y = size // 2, size // 2
            
            from PyQt5.QtGui import QPolygon
            from PyQt5.QtCore import QPoint
            
            triangle = QPolygon([
                QPoint(center_x - triangle_size // 2, center_y - triangle_size // 2),
                QPoint(center_x + triangle_size // 2, center_y),
                QPoint(center_x - triangle_size // 2, center_y + triangle_size // 2)
            ])
            painter.drawPolygon(triangle)
            
            # Draw filename
            painter.setPen(QColor(255, 255, 255))
            font = painter.font()
            font.setPixelSize(max(8, size // 15))
            painter.setFont(font)
            
            # Truncate filename if too long
            display_name = filename[:15] + "..." if len(filename) > 15 else filename
            text_rect = pixmap.rect()
            text_rect.setTop(text_rect.bottom() - 20)
            painter.drawText(text_rect, Qt.AlignCenter, display_name)
            
            if painter.isActive():
                painter.end()
            
            return self._add_rounded_corners(pixmap, 8)
        except Exception as e:
            print(f"Warning: Failed to create video placeholder: {e}")
            # Return simple colored rectangle as fallback
            fallback = QPixmap(size, size)
            fallback.fill(QColor(45, 45, 45))
            return fallback
    
    def _create_error_thumbnail(self, size: int, error_text: str) -> QPixmap:
        """Create an error placeholder thumbnail"""
        try:
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(60, 60, 60))
            
            painter = QPainter(pixmap)
            if not painter.isActive():
                return pixmap
                
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw error icon (X)
            painter.setPen(QColor(200, 100, 100))
            pen = painter.pen()
            pen.setWidth(3)
            painter.setPen(pen)
            
            margin = size // 4
            painter.drawLine(margin, margin, size - margin, size - margin)
            painter.drawLine(size - margin, margin, margin, size - margin)
            
            # Draw error text
            font = painter.font()
            font.setPixelSize(max(8, size // 20))
            painter.setFont(font)
            painter.setPen(QColor(255, 255, 255))
            
            text_rect = pixmap.rect()
            text_rect.setTop(text_rect.bottom() - 20)
            painter.drawText(text_rect, Qt.AlignCenter, error_text)
            
            if painter.isActive():
                painter.end()
            
            return self._add_rounded_corners(pixmap, 8)
        except Exception as e:
            print(f"Warning: Failed to create error thumbnail: {e}")
            # Return simple colored rectangle as fallback
            fallback = QPixmap(size, size)
            fallback.fill(QColor(60, 60, 60))
            return fallback
    
    def _add_rounded_corners(self, pixmap: QPixmap, radius: int) -> QPixmap:
        """Add rounded corners to pixmap"""
        try:
            if pixmap.isNull():
                return pixmap
                
            rounded = QPixmap(pixmap.size())
            rounded.fill(Qt.transparent)
            
            painter = QPainter(rounded)
            if not painter.isActive():
                return pixmap
                
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Create rounded rectangle path
            from PyQt5.QtGui import QPainterPath
            from PyQt5.QtCore import QRectF
            path = QPainterPath()
            rect = QRectF(rounded.rect())  # Convert QRect to QRectF
            path.addRoundedRect(rect, radius, radius)
            
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, pixmap)
            
            # Ensure painter is properly ended
            if painter.isActive():
                painter.end()
            
            return rounded
        except Exception as e:
            # If rounded corners fail, return original pixmap
            print(f"Warning: Failed to add rounded corners: {e}")
            return pixmap
    
    def _get_cache_path(self, file_path: str, size: int) -> str:
        """Get cache file path for thumbnail"""
        # Create hash from file path and size
        hash_input = f"{file_path}_{size}".encode('utf-8')
        file_hash = hashlib.md5(hash_input).hexdigest()
        return os.path.join(self.cache_dir, f"thumb_{file_hash}.png")
    
    def _get_cached_thumbnail(self, file_path: str, size: int) -> Optional[QPixmap]:
        """Get cached thumbnail if available and valid"""
        if not self.config.is_cache_enabled():
            return None
        
        cache_path = self._get_cache_path(file_path, size)
        
        try:
            if os.path.exists(cache_path):
                # Check if cache is newer than original file
                cache_mtime = os.path.getmtime(cache_path)
                file_mtime = os.path.getmtime(file_path)
                
                if cache_mtime > file_mtime:
                    pixmap = QPixmap(cache_path)
                    if not pixmap.isNull():
                        return pixmap
        except Exception:
            pass
        
        return None
    
    def _cache_thumbnail(self, file_path: str, thumbnail: QPixmap, size: int):
        """Cache thumbnail to disk"""
        try:
            cache_path = self._get_cache_path(file_path, size)
            thumbnail.save(cache_path, "PNG")
        except Exception:
            pass  # Ignore cache errors
    
    def clear_cache(self):
        """Clear thumbnail cache"""
        try:
            cache_dir = self.cache_dir
            for filename in os.listdir(cache_dir):
                if filename.startswith('thumb_') and filename.endswith('.png'):
                    os.remove(os.path.join(cache_dir, filename))
        except Exception:
            pass
    
    def get_cache_size(self) -> int:
        """Get cache size in bytes"""
        total_size = 0
        try:
            cache_dir = self.cache_dir
            for filename in os.listdir(cache_dir):
                if filename.startswith('thumb_') and filename.endswith('.png'):
                    file_path = os.path.join(cache_dir, filename)
                    total_size += os.path.getsize(file_path)
        except Exception:
            pass
        return total_size