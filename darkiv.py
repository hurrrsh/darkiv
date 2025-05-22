#!/usr/bin/env python3
"""
Usage: python darkiv.py input.pdf [output.pdf]
"""
# requirements: sudo apt-get install imagemagick poppler-utils
# pip install img2pdf
# works pretty quick with arxiv papers(usuall 10-15 pages), but on books pdfs takes time(around 5-10 mins for 300 pgs, but works well)

import sys
import os
import tempfile
import subprocess
from pathlib import Path

def convert_to_dark_mode(input_path, output_path=None):
    """convert a PDF to dark mode using Poppler and ImageMagick."""
    if output_path is None:
        input_path = Path(input_path)
        output_path = input_path.with_stem(f"{input_path.stem}_darkiv")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        print("extracting PDF pages as images...")
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
        
        print("combining inverted pages into PDF...")
        
        subprocess.run([
            "img2pdf",
            "--output", str(output_path),
            *dark_mode_images
        ])
        
        print(f"created successfully: {output_path}")
        return True

def main():
    print(r"""
        .___             __   .__       
      __| _/____ _______|  | _|__|__  __
     / __ |\__  \\_  __ \  |/ /  \  \/ /
    / /_/ | / __ \|  | \/    <|  |\   / 
    \____ |(____  /__|  |__|_ \__| \_/  
         \/     \/           \/         
    """)
    
    if len(sys.argv) < 2:
        print("usage: python darkiv.py input.pdf [output.pdf]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    if not os.path.exists(input_path):
        print(f"Error: The file '{input_path}' does not exist.")
        sys.exit(1)
    
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = convert_to_dark_mode(input_path, output_path)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
