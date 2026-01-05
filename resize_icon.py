"""Resize color.png to 192x192 pixels with white borders"""
from PIL import Image

def resize_with_padding(input_path, output_path, target_size=(192, 192), background_color=(255, 255, 255)):
    """Resize image to target size, adding white padding to maintain aspect ratio."""
    
    # Open the original image
    img = Image.open(input_path)
    original_size = img.size
    print(f"Original size: {original_size[0]}x{original_size[1]}")
    
    # Convert to RGBA if needed (to handle transparency)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Calculate the scaling factor to fit within target size
    ratio = min(target_size[0] / img.size[0], target_size[1] / img.size[1])
    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
    
    # Resize the image maintaining aspect ratio
    img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # Create a new image with white background
    new_img = Image.new('RGBA', target_size, background_color + (255,))
    
    # Calculate position to center the resized image
    position = ((target_size[0] - new_size[0]) // 2, (target_size[1] - new_size[1]) // 2)
    
    # Paste the resized image onto the white background
    new_img.paste(img_resized, position, img_resized)
    
    # Convert to RGB for PNG without alpha issues
    final_img = Image.new('RGB', target_size, background_color)
    final_img.paste(new_img, mask=new_img.split()[3])
    
    # Save the result
    final_img.save(output_path, 'PNG')
    print(f"Saved resized image: {output_path} ({target_size[0]}x{target_size[1]})")

if __name__ == "__main__":
    input_file = r"c:\Users\fizamusthafa\AgentsToolkitProjects\cosmosdb_copilot\appPackage\color.png"
    output_file = r"c:\Users\fizamusthafa\AgentsToolkitProjects\cosmosdb_copilot\appPackage\color.png"
    
    resize_with_padding(input_file, output_file, target_size=(192, 192))
    print("Done!")
