from PIL import Image
import numpy as np
from rembg import remove
import os
from extract_image import extract_all_facet_graphs, extract_first_graph, extract_dominant_graph


def remove_background_colors(img_path, target_colors, tolerance=60, output_path=None):
    """
    Remove specific background colors from an image and replace them with white.

    :param img_path: Path to the input image.
    :param target_colors: List of RGB tuples of the target colors to remove.
    :param tolerance: Tolerance for color matching.
    :param output_path: Path to save the output image. If None, saves in the same directory as input.
    """
    try:
        # Load the image
        img = Image.open(img_path).convert("RGBA")
        data = np.array(img)

        # Iterate over each target color
        for target_color in target_colors:
            # Define the target color
            target_color = np.array(target_color)

            # Compute distance from target color
            rgb = data[..., :3]
            distance = np.linalg.norm(rgb - target_color, axis=-1)

            # Create mask where distance is within tolerance
            mask = distance < tolerance

            # Set RGB to white where mask is True
            data[..., :3][mask] = [255, 255, 255]
        white_mask = np.all(data[..., :3] == [255, 255, 255], axis=-1)
        data[..., 3][white_mask] = 0

        blue_mask = np.all(data[..., :3] == [213, 232, 228], axis=-1)
        data[..., 3][blue_mask] = 0
        # Convert back to image
        output_img = Image.fromarray(data)
        # output_img = remove(output_img)

        # Determine output path
        if output_path is None:
            output_path = img_path.replace('.jpeg', '_with_white_background.png')

        # Save result
        output_img.save(output_path)
        print(f"Image saved to {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


def crop_image(img_path, crop_box, output_path=None):
    """
    Crop a section of an image.

    :param img_path: Path to the input image.
    :param crop_box: A tuple (left, upper, right, lower) defining the box to crop.
    :param output_path: Path to save the cropped image. If None, saves in the same directory as input.
    """
    try:
        # Load the image
        img = Image.open(img_path)

        # Crop the image
        cropped_img = img.crop(crop_box)

        # Determine output path
        if output_path is None:
            output_path = img_path.replace('.png', '_cropped.png')

        # Save the cropped image
        cropped_img.save(output_path)
        print(f"Cropped image saved to {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


def convert_blue_to_red(image_path: str, output_path: str) -> None:
    """
    Converts all blue-dominant pixels in an image to red-dominant pixels and ensures they are 3 pixels wide.
    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the output image.
    """

    # Load image and convert to RGBA
    img = Image.open(image_path).convert("RGBA")
    data = np.array(img)

    # Extract RGB channels
    r, g, b, a = data.T

    # Define condition for blue-dominant pixels
    blue_mask = (b > r) & (b > g)

    # Convert blue to red: R = B, G = 0, B = 0
    data[..., 0][blue_mask.T] = b[blue_mask]
    data[..., 1][blue_mask.T] = 0
    data[..., 2][blue_mask.T] = 0

    # Save the result
    Image.fromarray(data).save(output_path)


def convert_to_pure_blue(image_path: str, output_path: str) -> None:
    img = Image.open(image_path).convert("RGBA")
    data = np.array(img)
    # Extract RGB channels
    r, g, b, a = data.T

    # Define condition for blue-dominant pixels
    blue_mask = (b > r) & (b > g)

    # Convert to pure blue: R = 0, G = 0, B = B
    data[..., 0][blue_mask.T] = 0
    data[..., 1][blue_mask.T] = 0
    data[..., 2][blue_mask.T] = b[blue_mask]

    # Save the result
    Image.fromarray(data).save(output_path)


def create_red_graph(image_path: str, output_path: str, identifier: str) -> None:
    # Ensure the directory exists before any file operations
    tmp_dir = os.path.dirname(output_path)
    ensure_directory_exists(tmp_dir)

    # Define the path for the cropped image
    cropped_output_path = os.path.join(tmp_dir, f'{identifier}_red_cropped.png')
    crop_box = (231, 134, 748, 449)
    
    # Crop the image and save it to the cropped_output_path
    crop_image(image_path, crop_box, output_path=cropped_output_path)

    # Debugging output
    print(f"Cropped image path: {cropped_output_path}")
    print(f"Output path for red graph: {output_path}")

    background_colors = [(193, 206, 228), (216, 224, 199), (0, 0, 0), (255, 255, 255),
                         (45, 34, 14), (154, 143, 141), (255, 246, 216), (215, 234, 230),
                         (185, 224, 255), (133, 195, 246), (122, 123, 118)]
    remove_background_colors(cropped_output_path, background_colors, tolerance=35)
    convert_blue_to_red(cropped_output_path, output_path=output_path)


def create_blue_graph(image_path: str, output_path: str, identifier: str) -> None:
    # Ensure the directory exists before any file operations
    tmp_dir = os.path.dirname(output_path)
    ensure_directory_exists(tmp_dir)
    crop_box = (231, 134, 748, 449)
    cropped_output_path = os.path.join(tmp_dir, f'{identifier}_cropped_image_blue.png')
    crop_image(image_path, crop_box, output_path=cropped_output_path)
    background_colors = [(193, 206, 228), (216, 224, 199), (188, 202, 161), (0, 0, 0), (255, 255, 255),
                         (45, 34, 14), (154, 143, 141), (255, 246, 216), (28, 47, 64), (215, 234, 230), (167, 190, 217),
                         (185, 224, 255), (133, 195, 246), (122, 123, 118)]
    remove_background_colors(cropped_output_path, background_colors, tolerance=35)
    convert_to_pure_blue(cropped_output_path, output_path=output_path)


def overlay_images(background_path, overlay_path, output_path, position=(0, 0)):
    background = Image.open(background_path).convert("RGBA")
    overlay = Image.open(overlay_path).convert("RGBA")

    background.paste(overlay, position, overlay)
    background.save(output_path)


def ensure_directory_exists(directory_path):
    """Ensure that a directory exists; if not, create it."""
    os.makedirs(directory_path, exist_ok=True)


def resize_image(image_path, output_path, scale_factor=2):
    """
    Resize an image by a given scale factor while preserving the original red and blue color values
    and maintaining the organic, wavy look.
    
    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the resized image.
        scale_factor (float): Factor by which to scale the image.
    """
    # Load the image
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)

    # Resize using nearest neighbor to maintain sharp edges
    resized_img = img.resize((new_width, new_height), Image.NEAREST)

    # Convert to numpy array for pixel manipulation
    data = np.array(resized_img)

    # Extract RGB channels
    r, g, b, a = data.T

    # Create masks for red-dominant and blue-dominant pixels
    red_dominant = (r > g) & (r > b) & (a > 0)
    blue_dominant = (b > r) & (b > g) & (a > 0)

    # Set all non-red-dominant, non-blue-dominant pixels to transparent
    transparent_mask = ~(red_dominant | blue_dominant)
    data[..., 3][transparent_mask.T] = 0  # Set alpha to 0 for transparent pixels

    # For red-dominant pixels, preserve the red value but zero out green and blue
    data[..., 1][red_dominant.T] = 0
    data[..., 2][red_dominant.T] = 0

    # For blue-dominant pixels, preserve the blue value but zero out red and green
    data[..., 0][blue_dominant.T] = 0
    data[..., 1][blue_dominant.T] = 0

    # Convert back to image and save
    result_img = Image.fromarray(data)
    result_img.save(output_path)


def create_dual_facet_graphs(first_pdf_path, second_pdf_path, output_dir=None):
    """
    Creates dual facet graphs (red and blue overlaid) for two PDFs.
    
    Args:
        first_pdf_path (str): Path to the first PDF (will be rendered in red)
        second_pdf_path (str): Path to the second PDF (will be rendered in blue)
        output_dir (str, optional): Directory to save output files. If None, uses default tmp directory.
    
    Returns:
        dict: Dictionary with graph types as keys and paths to final images as values
    """
    # Extract the first 6 letters of each file name for identifier
    first_name_part = os.path.basename(first_pdf_path)[:6]
    first_name = os.path.basename(first_pdf_path).replace('.pdf', '')
    second_name_part = os.path.basename(second_pdf_path)[:6]
    second_name = os.path.basename(second_pdf_path).replace('.pdf', '')
    identifier = f"{first_name_part}_{second_name_part}"

    # Set up directories
    if output_dir is None:
        output_dir = rf'F:\projects\MBTInfo\backend\media\tmp'

    tmp_dir = output_dir
    final_dir = os.path.join(tmp_dir, 'final')
    ensure_directory_exists(tmp_dir)
    ensure_directory_exists(final_dir)

    print(f"Extracting graphs from {first_name_part}'s PDF...")
    first_pdf_output_dir = os.path.join(output_dir, first_name)
    extract_all_facet_graphs(first_pdf_path, output_dir)

    print(f"Extracting graphs from {second_name_part}'s PDF...")
    second_pdf_output_dir = os.path.join(output_dir, second_name)
    extract_all_facet_graphs(second_pdf_path, output_dir)

    # List of graph types to process
    graph_types = ["EIGraph", "SNgraph", "TFgraph", "JPgraph"]

    # Dictionary to store output paths
    output_paths = {}

    # Process each graph type
    for graph_type in graph_types:
        print(f"Processing {graph_type}...")

        # Define background image path based on graph type
        background_path = rf'F:\projects\MBTInfo\backend\media\Dual_Report_Media\backgrounds\background{graph_type[:2]}.jpeg'

        # Define paths for first and second PDFs' graphs
        page_num = 5 if graph_type == "EIGraph" else 6 if graph_type == "SNgraph" else 7 if graph_type == "TFgraph" else 8

        first_graph_path = os.path.join(first_pdf_output_dir, "screenshots", f"page{page_num}_{graph_type}.png")
        second_graph_path = os.path.join(second_pdf_output_dir, "screenshots", f"page{page_num}_{graph_type}.png")

        # Create red and blue graphs with initial processing
        red_output_path = os.path.join(tmp_dir, f'{identifier}_{graph_type}_red.png')
        blue_output_path = os.path.join(tmp_dir, f'{identifier}_{graph_type}_blue.png')

        create_red_graph(first_graph_path, output_path=red_output_path, identifier=identifier)
        create_blue_graph(second_graph_path, output_path=blue_output_path, identifier=identifier)

        # Resize the images
        resized_red_path = os.path.join(tmp_dir, f'{identifier}_{graph_type}_red_resized.png')
        resized_blue_path = os.path.join(tmp_dir, f'{identifier}_{graph_type}_blue_resized.png')

        resize_image(red_output_path, resized_red_path, scale_factor=1.66)
        resize_image(blue_output_path, resized_blue_path, scale_factor=1.66)

        # Combine the enhanced graphs
        combined_path = os.path.join(tmp_dir, f'{identifier}_{graph_type}_combined.png')
        overlay_images(resized_blue_path, resized_red_path, combined_path, position=(0, 9))

        # Create final output with background
        final_output_path = os.path.join(final_dir, f'{identifier}_{graph_type}_final.png')
        overlay_images(background_path, combined_path, final_output_path, position=(375, 170))

        # Store the output path
        output_paths[graph_type] = final_output_path

        print(f"Completed {graph_type} graph")

    print("All graphs created successfully!")
    return output_paths


def create_first_graph(first_pdf_path, second_pdf_path, output_dir):
    first_name_part = os.path.basename(first_pdf_path)[:6]
    second_name_part = os.path.basename(second_pdf_path)[:6]
    identifier = f"{first_name_part}_{second_name_part}"
    background_path = r"F:\projects\MBTInfo\backend\media\Dual_Report_Media\backgrounds\page3_graph.png"
    
    # Set up directories
    if output_dir is None:
        output_dir = rf'F:\projects\MBTInfo\backend\media\tmp'

    tmp_dir = output_dir
    final_dir = os.path.join(tmp_dir, 'final')
    ensure_directory_exists(tmp_dir)
    ensure_directory_exists(final_dir)

    print(f"Extracting graph from {first_name_part}'s PDF...")
    print(f"Extracting graph from {second_name_part}'s PDF...")
    target_colors = [(192, 208, 167), (206, 218, 187), (178, 197, 148), (164, 187, 129), (0, 0, 0), (255, 255, 255)]
    first_graph_one_path = extract_first_graph(first_pdf_path, tmp_dir)
    first_graph_two_path = extract_first_graph(second_pdf_path, tmp_dir)
    remove_background_colors(first_graph_one_path, target_colors, tolerance=60)
    remove_background_colors(first_graph_two_path, target_colors, tolerance=60)

    convert_blue_to_red(first_graph_one_path, rf"{tmp_dir}\first_graph_one_red.png")
    convert_to_pure_blue(first_graph_two_path, rf"{tmp_dir}\first_graph_two_blue.png")

    resized_red_path = os.path.join(tmp_dir, f'{identifier}_one_red_resized.png')
    resized_blue_path = os.path.join(tmp_dir, f'{identifier}_two_blue_resized.png')

    resize_image(rf"{tmp_dir}\first_graph_one_red.png", resized_red_path, scale_factor=2.1)
    resize_image(rf"{tmp_dir}\first_graph_two_blue.png", resized_blue_path, scale_factor=2.1)

    overlay_images(resized_blue_path, resized_red_path, rf"{tmp_dir}\first_graph_combined.png", position=(0, 12))
    overlay_images(background_path, rf"{tmp_dir}\first_graph_combined.png", rf"{final_dir}\{identifier}_first_graph_final.png", position=(392, 88))
    return rf"{final_dir}\{identifier}_first_graph_final.png"


def create_dominant_graph(first_pdf_path, second_pdf_path, output_dir):
    first_name_part = os.path.basename(first_pdf_path)[:6]
    second_name_part = os.path.basename(second_pdf_path)[:6]
    identifier = f"{first_name_part}_{second_name_part}"
    background_path = r"F:\projects\MBTInfo\backend\media\Dual_Report_Media\backgrounds\white_1180x417.png"
    
    # Set up directories
    if output_dir is None:
        output_dir = rf'F:\projects\MBTInfo\backend\media\tmp'

    tmp_dir = output_dir
    final_dir = os.path.join(tmp_dir, 'final')
    ensure_directory_exists(tmp_dir)
    ensure_directory_exists(final_dir)

    print(f"Extracting graph from {first_name_part}'s PDF...")
    print(f"Extracting graph from {second_name_part}'s PDF...")
    dom_graph_one_path = extract_dominant_graph(first_pdf_path, tmp_dir)
    dom_graph_two_path = extract_dominant_graph(second_pdf_path, tmp_dir)
    target_colors = [(226, 234, 215)]
    remove_background_colors(dom_graph_one_path, target_colors, tolerance=60)
    remove_background_colors(dom_graph_two_path, target_colors, tolerance=60)
    print(rf"{tmp_dir}\dominant_graph_combined.png")
    overlay_images(background_path, dom_graph_one_path, rf"{tmp_dir}\dominant_graph_combined.png", position=(90, 69))
    overlay_images(rf"{tmp_dir}\dominant_graph_combined.png", dom_graph_two_path, rf"{final_dir}\{identifier}_dominant_graph_final.png", position=(634, 69))
    print(f"Creating final image for {identifier}'s dominant graph...")
    return rf"{final_dir}\{identifier}_dominant_graph_final.png"


def create_all_graphs(first_pdf_path, second_pdf_path, output_dir):
    facet_graphs = create_dual_facet_graphs(first_pdf_path, second_pdf_path, output_dir)
    first_graph = create_first_graph(first_pdf_path, second_pdf_path, output_dir)
    dominant_graph = create_dominant_graph(first_pdf_path, second_pdf_path, output_dir)
    print(f"All graphs created successfully! at:\n{output_dir}\\final")
    print(f"{facet_graphs}\n{first_graph}\n{dominant_graph}")
    return


if __name__ == '__main__':
    first_pdf_path = r'F:\projects\MBTInfo\input\ADAM-POMERANTZ-267149-e4b6edb5-1a5f-ef11-bdfd-6045bd04b01a.pdf'
    second_pdf_path = r'F:\projects\MBTInfo\input\Adi-Chen-267149-30ffb71f-a3fd-ef11-90cb-000d3a58c2b2.pdf'

    # Extract identifier based on both filenames
    first_name_part = os.path.basename(first_pdf_path).replace('.pdf', '')[:6]
    second_name_part = os.path.basename(second_pdf_path).replace('.pdf', '')[:6]
    identifier = f"{first_name_part}_{second_name_part}"

    # Set unified output directory
    output_dir = os.path.join(r"F:\projects\MBTInfo\backend\media\tmp", identifier)

    # Run full graph generation
    create_all_graphs(first_pdf_path, second_pdf_path, output_dir)