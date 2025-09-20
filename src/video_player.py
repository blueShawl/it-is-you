#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Video Player Widget
Basic video playback functionality for the photo viewer
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QSlider, QFrame, QSizePolicy,
                             QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QUrl
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

from .photo_scanner import PhotoInfo


class VideoPlayerWidget(QWidget):
    """Simple video player widget"""
    
    # Signals
    closed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.media_player = None
        self.video_widget = None
        self.current_video = None
        self.setup_ui()
        self.setup_media_player()
        
    def setup_ui(self):
        """Setup the video player UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Video display area
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("""
            QFrame {
                background-color: #000000;
                border: none;
            }
        """)
        self.video_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        video_layout = QVBoxLayout(self.video_frame)
        video_layout.setContentsMargins(0, 0, 0, 0)
        
        # Video widget
        try:
            self.video_widget = QVideoWidget()
            self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            video_layout.addWidget(self.video_widget)
        except Exception:
            # Fallback if video widget is not available
            self.video_placeholder = QLabel("Video playback not supported")
            self.video_placeholder.setAlignment(Qt.AlignCenter)
            self.video_placeholder.setStyleSheet("color: white; font-size: 18px;")
            video_layout.addWidget(self.video_placeholder)
        
        layout.addWidget(self.video_frame)
        
        # Controls
        self.create_controls(layout)
    
    def create_controls(self, parent_layout):
        """Create video control widgets"""
        controls_frame = QFrame()
        controls_frame.setFixedHeight(80)
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-top: 1px solid #404040;
            }
        """)
        
        layout = QVBoxLayout(controls_frame)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(8)
        
        # Progress slider
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setEnabled(False)
        self.progress_slider.sliderPressed.connect(self.on_seek_start)
        self.progress_slider.sliderReleased.connect(self.on_seek_end)
        layout.addWidget(self.progress_slider)
        
        # Control buttons and info
        button_layout = QHBoxLayout()
        
        # Play/Pause button
        self.play_button = QPushButton("Play")
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self.toggle_playback)
        button_layout.addWidget(self.play_button)
        
        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_playback)
        button_layout.addWidget(self.stop_button)
        
        button_layout.addStretch()
        
        # Time display
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setProperty("labelStyle", "caption")
        button_layout.addWidget(self.time_label)
        
        button_layout.addStretch()
        
        # Volume control
        volume_label = QLabel("Volume:")
        volume_label.setProperty("labelStyle", "caption")
        button_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        button_layout.addWidget(self.volume_slider)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close_video)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        parent_layout.addWidget(controls_frame)
    
    def setup_media_player(self):
        """Setup media player"""
        try:
            self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
            
            if self.video_widget:
                self.media_player.setVideoOutput(self.video_widget)
            
            # Connect signals
            self.media_player.stateChanged.connect(self.on_state_changed)
            self.media_player.positionChanged.connect(self.on_position_changed)
            self.media_player.durationChanged.connect(self.on_duration_changed)
            self.media_player.error.connect(self.on_media_error)
            
            # Setup update timer
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.update_ui)
            self.update_timer.start(100)  # Update every 100ms
            
        except Exception as e:
            self.show_error(f"Failed to initialize media player: {str(e)}")
    
    def load_video(self, photo_info: PhotoInfo):
        """Load and play video file"""
        if not self.media_player:
            self.show_error("Media player not available")
            return
        
        if not os.path.exists(photo_info.file_path):
            self.show_error("Video file not found")
            return
        
        self.current_video = photo_info
        
        try:
            # Load media
            media_content = QMediaContent(QUrl.fromLocalFile(photo_info.file_path))
            self.media_player.setMedia(media_content)
            
            # Update UI
            self.setWindowTitle(f"Video Player - {photo_info.file_name}")
            
            # Enable controls
            self.play_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.progress_slider.setEnabled(True)
            
            # Set volume
            self.media_player.setVolume(self.volume_slider.value())
            
        except Exception as e:
            self.show_error(f"Failed to load video: {str(e)}")
    
    def toggle_playback(self):
        """Toggle play/pause"""
        if not self.media_player:
            return
        
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()
    
    def stop_playback(self):
        """Stop playback"""
        if self.media_player:
            self.media_player.stop()
    
    def set_volume(self, volume):
        """Set playback volume"""
        if self.media_player:
            self.media_player.setVolume(volume)
    
    def on_state_changed(self, state):
        """Handle playback state changes"""
        if state == QMediaPlayer.PlayingState:
            self.play_button.setText("Pause")
        else:
            self.play_button.setText("Play")
    
    def on_position_changed(self, position):
        """Handle playback position changes"""
        if not self.progress_slider.isSliderDown():
            self.progress_slider.setValue(position)
        
        self.update_time_display(position)
    
    def on_duration_changed(self, duration):
        """Handle duration changes"""
        self.progress_slider.setRange(0, duration)
        self.update_time_display(self.media_player.position() if self.media_player else 0)
    
    def on_seek_start(self):
        """Handle seek start"""
        pass  # Slider position updates are handled automatically
    
    def on_seek_end(self):
        """Handle seek end"""
        if self.media_player:
            self.media_player.setPosition(self.progress_slider.value())
    
    def on_media_error(self, error):
        """Handle media playback errors"""
        error_messages = {
            QMediaPlayer.NoError: "No error",
            QMediaPlayer.ResourceError: "Resource error - file may be corrupted or unsupported",
            QMediaPlayer.FormatError: "Format error - unsupported video format",
            QMediaPlayer.NetworkError: "Network error",
            QMediaPlayer.AccessDeniedError: "Access denied",
            QMediaPlayer.ServiceMissingError: "Media service missing"
        }
        
        message = error_messages.get(error, f"Unknown error ({error})")
        self.show_error(f"Playback error: {message}")
    
    def update_ui(self):
        """Update UI elements"""
        # This method can be used for periodic UI updates
        pass
    
    def update_time_display(self, position):
        """Update time display"""
        if not self.media_player:
            return
        
        duration = self.media_player.duration()
        
        # Format time
        def format_time(ms):
            seconds = ms // 1000
            minutes = seconds // 60
            seconds = seconds % 60
            return f"{minutes:02d}:{seconds:02d}"
        
        current_time = format_time(position)
        total_time = format_time(duration) if duration > 0 else "00:00"
        
        self.time_label.setText(f"{current_time} / {total_time}")
    
    def show_error(self, message):
        """Show error message"""
        QMessageBox.critical(self, "Video Player Error", message)
    
    def close_video(self):
        """Close video player"""
        if self.media_player:
            self.media_player.stop()
        
        self.current_video = None
        self.closed.emit()
    
    def closeEvent(self, event):
        """Handle close event"""
        self.close_video()
        event.accept()


class VideoPlayerDialog(QWidget):
    """Standalone video player dialog"""
    
    def __init__(self, photo_info: PhotoInfo, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Video Player - {photo_info.file_name}")
        self.setMinimumSize(800, 600)
        
        # Setup UI
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Video player
        self.player = VideoPlayerWidget()
        self.player.closed.connect(self.close)
        layout.addWidget(self.player)
        
        # Load video
        self.player.load_video(photo_info)
        
        # Show window
        self.show()


def play_video(photo_info: PhotoInfo, parent=None):
    """Convenience function to play video"""
    try:
        player_dialog = VideoPlayerDialog(photo_info, parent)
        return player_dialog
    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Could not play video: {str(e)}")
        return None