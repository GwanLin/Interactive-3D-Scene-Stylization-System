import open3d as o3d
import numpy as np

# Load the existing point cloud
input_ply = "2-ntust_style_texture/2_texture.ply"
pcd = o3d.io.read_point_cloud(input_ply)

# Check the number of points
print(f"Number of points: {len(pcd.points)}")

# Visualize the updated point cloud
o3d.visualization.draw_geometries([pcd])
