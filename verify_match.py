import json
import os
import subprocess
import sys
from PIL import Image
import numpy as np

# Load the dataset
with open('asymp_dataset.json', 'r') as f:
    data = json.load(f)

# Check command line arguments
if len(sys.argv) > 1:
    try:
        idx = int(sys.argv[1])
        if idx < 0 or idx >= len(data):
            print(f"Index out of range. Please provide a value between 0 and {len(data) - 1}")
            sys.exit(1)
    except ValueError:
        print("Please provide a valid integer index")
        sys.exit(1)
else:
    # Default to entry 10
    idx = 10

print(f"Verifying entry {idx}:")
print(f"Image path: {data[idx]['image_path']}")
print(f"Code snippet (first 100 chars):\n{data[idx]['code'][:100]}...")

# Check if the image exists
if not os.path.exists(data[idx]['image_path']):
    print("ERROR: Image does not exist!")
    sys.exit(1)

# Create a temporary directory for verification
os.makedirs('verify_temp', exist_ok=True)

# Extract the code and save to a temporary file
temp_asy = 'verify_temp/temp.asy'
with open(temp_asy, 'w') as f:
    f.write(data[idx]['code'])

# Create a new PNG from the code
temp_png = 'verify_temp/temp.png'
print("\nRendering code to a new image...")
cmd = ["asy", "-f", "png", "-o", temp_png, "-texpath", "/Library/TeX/texbin", temp_asy]
try:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error rendering the code:")
        print(result.stderr)
        sys.exit(1)
    
    # Check if the output has .png.png extension
    if os.path.exists(temp_png + '.png'):
        os.rename(temp_png + '.png', temp_png)
        
    if not os.path.exists(temp_png):
        print("Error: Failed to generate image from code")
        sys.exit(1)
    
    print("Successfully rendered the code to a new image")
    
    # Optional: Compare the images
    try:
        original_img = Image.open(data[idx]['image_path'])
        new_img = Image.open(temp_png)
        
        print(f"\nOriginal image size: {original_img.size}")
        print(f"New image size: {new_img.size}")
        
        # If sizes are very different, they're likely different images
        width_ratio = original_img.width / new_img.width
        height_ratio = original_img.height / new_img.height
        
        if width_ratio < 0.8 or width_ratio > 1.2 or height_ratio < 0.8 or height_ratio > 1.2:
            print("\nWARNING: Image dimensions are significantly different!")
        else:
            print("\nImage dimensions are reasonably similar.")
        
        print("\nVerification complete. Please manually check:")
        print(f"1. Original image: {data[idx]['image_path']}")
        print(f"2. Newly rendered image: {temp_png}")
    except Exception as e:
        print(f"Error comparing images: {str(e)}")
        
except Exception as e:
    print(f"Error running Asymptote: {str(e)}") 