# Texture Implementation for 3D Style Transfer

This source code provides the code and resources for extending PSNet's 3D style transfer capabilities with a texture implementation as a post-processing step.

---

# Requirements

- Python Version: 3.7.9
- Development Environment: Visual Studio Code
- Required Libraries:
  python
  import open3d as o3d
  import numpy as np
  from PIL import Image, ImageFilter
  from torchvision import transforms
  from colorsys import rgb_to_hsv, hsv_to_rgb

# File Components

This project contains two main Python scripts for running and visualizing the 3D style transfer process:

1. **`3d_open.py`**  
   - Purpose: Script for visualizing 3D models.
   - Usage: Use this script to open and inspect `.ply` files after processing.

2. **`3d_ply_style_wall_texture.py`**  
   - Purpose: Core implementation script for applying texture overlays onto the 3D styled models.
   - Usage: Adjust the input `.ply` files, style images, and save locations for the results directly in this script.

## Input and Output Management

**Input Style and Texture Images:**  
Style images and textures are numbered from `1` to `9`. To experiment with different styles or textures, simply change the number in the corresponding file paths (e.g., `1style.png`, `2style.png`, etc.).
  
**Saving Results:**  
The results are saved in the `2-ntust_style_texture/` folder. Ensure the paths for saving output files are correctly set in the scripts.


# How to Run
Step 1: Process Style Images
- Navigate to the 3-style_img/ folder.
- Run the processing scripts (process1.py, process2.py, etc.) to generate processed style images.
- Save the output images in the same folder.

Step 2: Detect and Process Wall Areas
- Run 3d_ply_style_wall_texture.py to detect walls using the stack_threshold parameter.
- Apply dilation to the wall mask using the dilation_radius parameter.
- The results will be saved in the 4-wall/ folder.

Step 3: Apply Texture Overlay
- Use the 3d_ply_style_wall_texture.py script to overlay textures on the 3D models.
- Adjust the technique parameter to select between "blend" and "saturation."
- The final textured models will be saved in the 2-ntust_style_texture/ folder.

Step 4: View Results
- Use 3d_open.py to visualize the textured 3D models.