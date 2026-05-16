import cv2
import numpy as np
import os

def remove_background(input_path, output_path):
    # Load image
    img = cv2.imread(input_path)
    if img is None:
        print(f"Could not load image at {input_path}")
        return

    # Convert to BGRA
    h, w = img.shape[:2]
    # Create mask for floodFill
    mask = np.zeros((h + 2, w + 2), np.uint8)
    
    # Copy of image for processing
    flood_img = img.copy()
    
    # Flood fill from 4 corners
    for start_point in [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1)]:
        cv2.floodFill(flood_img, mask, start_point, (255, 0, 255), (10, 10, 10), (10, 10, 10))
    
    # Create alpha channel based on the filled color (magenta)
    b, g, r = cv2.split(img)
    alpha = np.ones(b.shape, dtype=b.dtype) * 255
    
    # Pixels that were filled in flood_img are now (255, 0, 255)
    # Check where flood_img matches the fill color
    fill_mask = (flood_img[:,:,0] == 255) & (flood_img[:,:,1] == 0) & (flood_img[:,:,2] == 255)
    alpha[fill_mask] = 0
    
    # Combine back
    bgra = cv2.merge((b, g, r, alpha))
    
    # Save as PNG
    cv2.imwrite(output_path, bgra)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    base_dir = r"d:\TRI_TUE_NHAN_TAO\GAME_HAY\chien_truong\ANH"
    remove_background(os.path.join(base_dir, "temp_player.jpg"), os.path.join(base_dir, "player_clean.png"))
