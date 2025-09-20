#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Script for Modern Photo Viewer
Creates some sample images for testing the application
"""

import os
from PIL import Image, ImageDraw, ImageFont
import random
from datetime import datetime, timedelta


def create_sample_photos(output_dir: str, count: int = 20):
    """Create sample photos for testing"""
    
    # Create output directory structure
    folders = [
        "Photos/2024/January",
        "Photos/2024/February", 
        "Photos/2024/March",
        "Photos/Vacation/Beach",
        "Photos/Vacation/Mountains",
        "Photos/Family/Birthdays",
        "Photos/Family/Holidays"
    ]
    
    for folder in folders:
        full_path = os.path.join(output_dir, folder)
        os.makedirs(full_path, exist_ok=True)
    
    # Colors for sample images
    colors = [
        (255, 100, 100),  # Red
        (100, 255, 100),  # Green
        (100, 100, 255),  # Blue
        (255, 255, 100),  # Yellow
        (255, 100, 255),  # Magenta
        (100, 255, 255),  # Cyan
        (255, 150, 50),   # Orange
        (150, 100, 255),  # Purple
    ]
    
    # Sample names
    names = [
        "sunset", "landscape", "portrait", "flower", "building", "street",
        "nature", "beach", "mountain", "forest", "city", "park", "garden",
        "vacation", "family", "friends", "party", "dinner", "birthday"
    ]
    
    created_count = 0
    
    for i in range(count):
        # Choose random folder
        folder = random.choice(folders)
        full_folder_path = os.path.join(output_dir, folder)
        
        # Choose random properties
        width = random.randint(800, 1920)
        height = random.randint(600, 1080)
        color = random.choice(colors)
        name = random.choice(names)
        
        # Create image
        image = Image.new('RGB', (width, height), color)
        draw = ImageDraw.Draw(image)
        
        # Add some shapes for visual interest
        for _ in range(random.randint(3, 8)):
            shape_type = random.choice(['rectangle', 'ellipse'])
            x1 = random.randint(0, width // 2)
            y1 = random.randint(0, height // 2)
            x2 = random.randint(width // 2, width)
            y2 = random.randint(height // 2, height)
            
            shape_color = tuple(random.randint(0, 255) for _ in range(3))
            
            if shape_type == 'rectangle':
                draw.rectangle([x1, y1, x2, y2], fill=shape_color)
            else:
                draw.ellipse([x1, y1, x2, y2], fill=shape_color)
        
        # Add text
        try:
            # Try to add text with title
            text = f"{name}_{i+1:03d}"
            text_color = (255, 255, 255) if sum(color) < 400 else (0, 0, 0)
            
            # Draw text in center
            text_x = width // 2 - 50
            text_y = height // 2 - 20
            draw.text((text_x, text_y), text, fill=text_color)
            
        except:
            pass  # If font loading fails, skip text
        
        # Save image
        filename = f"{name}_{i+1:03d}.jpg"
        file_path = os.path.join(full_folder_path, filename)
        
        image.save(file_path, "JPEG", quality=85)
        
        # Set random creation time (within last year)
        days_ago = random.randint(1, 365)
        creation_time = datetime.now() - timedelta(days=days_ago)
        timestamp = creation_time.timestamp()
        
        # Set file modification time
        os.utime(file_path, (timestamp, timestamp))
        
        created_count += 1
        print(f"Created {filename} in {folder}")
    
    print(f"\nCreated {created_count} sample photos in {output_dir}")
    print("You can now test the Modern Photo Viewer with these images!")


if __name__ == "__main__":
    # Create sample photos in a test directory
    test_dir = "sample_photos"
    
    print("Creating sample photos for testing Modern Photo Viewer...")
    print(f"Output directory: {os.path.abspath(test_dir)}")
    
    create_sample_photos(test_dir, 30)
    
    print(f"\nTo test the application:")
    print("1. Run: python main.py")
    print(f"2. In settings, set photo path to: {os.path.abspath(test_dir)}")
    print("3. Click 'Scan Photos' to start!")