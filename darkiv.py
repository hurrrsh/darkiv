#!/usr/bin/env python3
"""
Usage: python pdf.py input.pdf [output.pdf]
"""

import sys
import os
import tempfile
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """Check if required command-line tools are installed"""
    missing = []
    try: subprocess.run(["pdftocairo", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError: missing.append("pdftocairo (poppler-utils)")
    
    try: subprocess.run(["convert", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError: missing.append("convert (ImageMagick)")
    
    try: subprocess.run(["img2pdf", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError: missing.append("img2pdf")

    if missing:
        print(f"ERROR: The following dependencies are missing: {', '.join(missing)}")
        print("\nInstallation instructions for Pop!_OS / Ubuntu:")
        print("sudo apt-get update")
        
        if "pdftocairo (poppler-utils)" in missing:
            print("sudo apt-get install -y poppler-utils")
        
        if "convert (ImageMagick)" in missing:
            print("sudo apt-get install -y imagemagick")
        
        if "img2pdf" in missing:
            print("sudo apt-get install -y python3-pip")
            print("pip3 install img2pdf")
            
        return False
    return True

def create_progress_bar(current, total, width=50):
    """ASCII progress bar."""
    progress = int(width * current / total)
    bar = "█" * progress + "░" * (width - progress)
    percentage = int(100 * current / total)
    return f"\r|{bar}| {percentage}% ({current}/{total} pages)"

def get_page_count(pdf_path):
    """Get the number of pages in the PDF file."""
    try:
        result = subprocess.run(
            ["pdfinfo", pdf_path], 
            capture_output=True, 
            text=True
        )
        for line in result.stdout.split('\n'):
            if line.startswith('Pages:'):
                return int(line.split(':')[1].strip())
    except Exception:
        return None
    
    return None

def convert_to_dark_mode(input_path, output_path=None):
    """convert a PDF to dark mode using Poppler and ImageMagick."""
    if output_path is None:
        input_path = Path(input_path)
        output_path = input_path.with_stem(f"{input_path.stem}_darkiv")
    
    print(f"Converting {input_path} to dark mode...")
    
    page_count = get_page_count(input_path)
    if page_count is None:
        page_count = 0  # Unknown number of pages
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        print("Extracting PDF pages as images...")
        subprocess.run([
            "pdftocairo", 
            "-png",        # Output format
            "-r", "300",   # Resolution (DPI)
            input_path,    # Input PDF
            str(temp_dir_path / "page")  # Output filename prefix
        ])
        
        image_files = sorted(list(temp_dir_path.glob("page-*.png")))
        
        if not image_files:
            print("Error: No images were extracted from the PDF.")
            return False
        
        print("applying dark mode...")
        dark_mode_images = []
        
        for i, img_file in enumerate(image_files):
            dark_img_file = temp_dir_path / f"dark-{img_file.name}"
            
            subprocess.run([
                "convert",
                str(img_file),
                "-negate",                   # Invert colors
                "-background", "black",      # Set background to black
                "-alpha", "remove",          # Remove alpha channel
                "-alpha", "off",             # Ensure no alpha
                str(dark_img_file)
            ])
            
            dark_mode_images.append(str(dark_img_file))
            
            if page_count > 0:
                sys.stdout.write(create_progress_bar(i + 1, len(image_files)))
                sys.stdout.flush()
        
        print("\ncombining inverted pages into PDF...")
        
        subprocess.run([
            "img2pdf",
            "--output", str(output_path),
            *dark_mode_images
        ])
        
        print(f"created successfully: {output_path}")
        return True

def main():
    if len(sys.argv) < 2:
        print("usage: python pdf.py input.pdf [output.pdf]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    if not os.path.exists(input_path):
        print(f"Error: The file '{input_path}' does not exist.")
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = convert_to_dark_mode(input_path, output_path)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
