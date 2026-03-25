import open3d as o3d
import numpy as np
from PIL import Image, ImageFilter
from torchvision import transforms
from colorsys import rgb_to_hsv, hsv_to_rgb

def detect_wall_regions(pcd, stack_threshold=15, prefix=""):
    """
    Detect wall regions in the 3D point cloud.
    - `stack_threshold`: Minimum number of vertically stacked points to qualify as a wall.
    """
    points = np.asarray(pcd.points)
    if points.size == 0:
        raise ValueError("Point cloud has no points.")
    x, y, z = points[:, 0], points[:, 1], points[:, 2]
    x = np.round(x, decimals=2)
    y = np.round(y, decimals=2)
    unique_x = np.unique(x)
    unique_y = np.unique(y)
    stack_counts = np.zeros((len(unique_x), len(unique_y)), dtype=int)
    for i in range(len(points)):
        x_idx = np.searchsorted(unique_x, x[i])
        y_idx = np.searchsorted(unique_y, y[i])
        stack_counts[x_idx, y_idx] += 1
    binary_wall_mask = (stack_counts > stack_threshold).astype(np.uint8) * 255
    wall_image = Image.fromarray(binary_wall_mask.T).transpose(Image.FLIP_TOP_BOTTOM)
    wall_image.save(f"4-wall/{prefix}_wall_regions_detected.png")  # Save wall detection result
    return binary_wall_mask

def dilate_wall_mask(wall_mask, dilation_radius=25, prefix=""):
    """
    Dilate the wall mask to account for inaccuracies in point cloud data.
    - `dilation_radius`: Radius for dilating the wall mask.
    """
    wall_image = Image.fromarray(wall_mask)
    dilated_wall_image = wall_image.filter(ImageFilter.MaxFilter(size=dilation_radius * 2 + 1))
    dilated_wall_mask = (np.array(dilated_wall_image) > 0).astype(np.uint8) * 255
    Image.fromarray(dilated_wall_mask).save(f"4-wall/{prefix}_wall_regions_detected_dilate.png")  # Save dilated wall mask
    return dilated_wall_mask

def prepare_style_image(style_image_path, target_size, threshold=220):
    """
    Prepare the style image for overlay by resizing and applying a threshold.
    - `target_size`: The size to resize the style image (matches wall mask size).
    - `threshold`: Intensity threshold for binarizing the style image.
    """
    style_image = Image.open(style_image_path).convert('L')
    style_image = style_image.resize(target_size, Image.BILINEAR)
    style_image = np.array(style_image)
    binary_mask = (style_image < threshold).astype(np.uint8) * 255
    return binary_mask

def overlay_wall_on_style_image(style_image, wall_mask, prefix=""):
    """
    Overlay the wall mask on the style image to exclude wall areas.
    - Sets wall regions in the style image to 0.
    """
    if len(style_image.shape) == 2:
        style_image = np.stack([style_image] * 3, axis=-1)
    green_color = np.array([0, 255, 0], dtype=np.uint8)  # Debug color for wall
    debug_overlay_image = style_image.copy()
    debug_overlay_image[wall_mask > 0] = green_color
    Image.fromarray(debug_overlay_image).save(f"4-wall/{prefix}_wall_regions_detected_dilate_overlay_green.png")  # Debug image
    combined_mask = np.where(wall_mask > 0, 0, style_image[:, :, 0])
    Image.fromarray(combined_mask).save(f"4-wall/{prefix}_wall_regions_detected_dilate_overlay.png")  # Final overlay
    return combined_mask

def apply_overlay_from_style_image(pcd, style_image, overlay_color=[255.0/255, 102.0/255, 102.0/255], 
                                   blend_factor=0.5, processing_flag="blend"):
    """
    Apply the style image as an overlay to the 3D point cloud.
    - `overlay_color`: RGB color for blending (normalized to [0, 1]).
    - `blend_factor`: Blending ratio (0.0 = only original, 1.0 = only overlay).
    - `processing_flag`: "blend" for color blending, "saturation" for saturation increase.
    """
    overlay_color = np.array(overlay_color)
    style_image = np.flipud(style_image)  # Flip vertically
    style_image = np.rot90(style_image, k=-1)  # Rotate clockwise
    vertices = np.asarray(pcd.points)
    original_colors = np.asarray(pcd.colors)
    vertices_min = vertices.min(axis=0)
    vertices_max = vertices.max(axis=0)
    normalized_vertices = (vertices - vertices_min) / (vertices_max - vertices_min)
    u = (normalized_vertices[:, 0] * (style_image.shape[1] - 1)).astype(int)
    v = (normalized_vertices[:, 1] * (style_image.shape[0] - 1)).astype(int)
    mask_values = style_image[v, u]
    updated_colors = np.asarray(original_colors.copy())
    for i, mask_value in enumerate(mask_values):
        if mask_value.any() > 0:
            if processing_flag == "blend":
                updated_colors[i] = (1 - blend_factor) * updated_colors[i] + blend_factor * overlay_color
            elif processing_flag == "saturation":
                r, g, b = updated_colors[i]
                h, s, v = rgb_to_hsv(r, g, b)
                s = min(s + blend_factor, 0.9)
                updated_colors[i] = hsv_to_rgb(h, s, v)
    pcd.colors = o3d.utility.Vector3dVector(updated_colors)
    return pcd

def main():
    """
    Main script for 3D texture implementation.
    Adjust the parameters below as needed.
    """
    point_cloud_path = "1-ntust_styled/style2.ply"  # Input point cloud path
    style_image_path = "3-style_img/2style.png"  # Input style image path
    prefix = style_image_path.split("/")[-1].split("style")[0] + "style"

    pcd = o3d.io.read_point_cloud(point_cloud_path)
    print("Point cloud loaded successfully!")
    print(f"Number of points: {len(pcd.points)}")

    # Parameter to adjust: `stack_threshold` (wall detection sensitivity)
    wall_mask = detect_wall_regions(pcd, stack_threshold=15, prefix=prefix)

    # Parameter to adjust: `dilation_radius` (wall mask thickness)
    dilated_wall_mask = dilate_wall_mask(wall_mask, dilation_radius=25, prefix=prefix)

    # Parameter to adjust: `threshold` (style image binarization intensity)
    style_image = prepare_style_image(style_image_path, target_size=(wall_mask.shape[1], wall_mask.shape[0]), threshold=220)

    # Overlay the wall mask on the style image
    combined_style_image = overlay_wall_on_style_image(style_image, dilated_wall_mask, prefix=prefix)

    # Parameter to adjust: `processing_flag` ("blend" or "saturation")

    # RGB color values for different styles:
    # Style 4: [77.0/255, 255.0/255, 195.0/255]  # Light teal color
    # Style 6: [160.0/255, 169.0/255, 197.0/255]  # Soft lavender gray
    # Style 7: [233.0/255, 216.0/255, 233.0/255]  # Light pinkish purple
    # Style 8: [74.0/255, 102.0/255, 85.0/255]   # Muted greenish tone
    # Style 9: [255.0/255, 102.0/255, 102.0/255] # Bright coral red
    
    styled_pcd = apply_overlay_from_style_image(pcd, combined_style_image, blend_factor=0.5, processing_flag="saturation")

    o3d.visualization.draw_geometries([styled_pcd])
    o3d.io.write_point_cloud("2-ntust_style_texture/2_texture.ply", styled_pcd)

if __name__ == '__main__':
    main()
