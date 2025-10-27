import os

import numpy as np
from PIL import Image

from .extract_image import (
    extract_all_facet_graphs,
    extract_dominant_graph,
    extract_first_graph,
)
from .utils import sanitize_filename, sanitize_path_component


def remove_background_colors(img_path, target_colors, tolerance=60, output_path=None):
    """
    Remove specific background colors from an image and replace them with white.

    :param img_path: Path to the input image.
    :param target_colors: List of RGB tuples of the target colors to remove.
    :param tolerance: Tolerance for color matching.
    :param output_path: Path to save the output image. If None, saves in the same directory as input.
    """
    try:
        # Check if input file exists
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"Input image not found: {img_path}")

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
            output_path = img_path.replace(".jpeg", "_with_white_background.png")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save result
        output_img.save(output_path)
        print(f"DEBUG: Background colors removed, saved to: {output_path}")

    except Exception as e:
        print(f"An error occurred in remove_background_colors: {e}")
        raise


def crop_image(img_path, crop_box, output_path=None):
    """
    Crop a section of an image.

    :param img_path: Path to the input image.
    :param crop_box: A tuple (left, upper, right, lower) defining the box to crop.
    :param output_path: Path to save the cropped image. If None, saves in the same directory as input.
    """
    try:
        # Check if input file exists
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"Input image not found: {img_path}")

        # Load the image
        img = Image.open(img_path)

        # Crop the image
        cropped_img = img.crop(crop_box)

        # Determine output path
        if output_path is None:
            output_path = img_path.replace(".png", "_cropped.png")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save the cropped image
        cropped_img.save(output_path)
        print(f"DEBUG: Image cropped and saved to: {output_path}")

    except Exception as e:
        print(f"An error occurred in crop_image: {e}")
        raise


def convert_blue_to_red(image_path: str, output_path: str) -> None:
    """
    Converts all blue-dominant pixels in an image to red-dominant pixels and ensures they are 3 pixels wide.
    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the output image.
    """
    try:
        # Check if input file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Input image not found: {image_path}")

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

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save the result
        Image.fromarray(data).save(output_path)
        print(f"DEBUG: Blue to red conversion completed, saved to: {output_path}")

    except Exception as e:
        print(f"An error occurred in convert_blue_to_red: {e}")
        raise


def convert_to_pure_blue(image_path: str, output_path: str) -> None:
    try:
        # Check if input file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Input image not found: {image_path}")

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

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save the result
        Image.fromarray(data).save(output_path)
        print(f"DEBUG: Pure blue conversion completed, saved to: {output_path}")

    except Exception as e:
        print(f"An error occurred in convert_to_pure_blue: {e}")
        raise


def create_red_graph(image_path: str, output_path: str, identifier: str) -> None:
    try:
        print("DEBUG: Starting create_red_graph")
        print(f"  Input image: {image_path}")
        print(f"  Output path: {output_path}")
        print(f"  Identifier: {identifier}")

        # Check if input image exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Input image not found: {image_path}")

        # Ensure the directory exists before any file operations
        tmp_dir = os.path.dirname(output_path)
        ensure_directory_exists(tmp_dir)

        # Define the path for the cropped image
        cropped_output_path = os.path.join(tmp_dir, f"{identifier}_red_cropped.png")
        crop_box = (231, 134, 748, 449)

        print(f"DEBUG: About to crop image to: {cropped_output_path}")

        # Crop the image and save it to the cropped_output_path
        crop_image(image_path, crop_box, output_path=cropped_output_path)

        # Verify the cropped file was created
        if not os.path.exists(cropped_output_path):
            raise FileNotFoundError(
                f"Cropped image was not created: {cropped_output_path}"
            )

        print(f"DEBUG: Cropped image created successfully: {cropped_output_path}")

        background_colors = [
            (193, 206, 228),
            (216, 224, 199),
            (0, 0, 0),
            (255, 255, 255),
            (45, 34, 14),
            (154, 143, 141),
            (255, 246, 216),
            (215, 234, 230),
            (185, 224, 255),
            (133, 195, 246),
            (122, 123, 118),
        ]

        print("DEBUG: About to remove background colors")
        remove_background_colors(cropped_output_path, background_colors, tolerance=35)

        print("DEBUG: About to convert blue to red")
        convert_blue_to_red(cropped_output_path, output_path=output_path)

        print("DEBUG: create_red_graph completed successfully")

    except Exception as e:
        print(f"ERROR in create_red_graph: {e}")
        print(f"  Input image: {image_path}")
        print(f"  Output path: {output_path}")
        print(f"  Identifier: {identifier}")
        raise


def create_blue_graph(image_path: str, output_path: str, identifier: str) -> None:
    try:
        print("DEBUG: Starting create_blue_graph")
        print(f"  Input image: {image_path}")
        print(f"  Output path: {output_path}")
        print(f"  Identifier: {identifier}")

        # Check if input image exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Input image not found: {image_path}")

        # Ensure the directory exists before any file operations
        tmp_dir = os.path.dirname(output_path)
        ensure_directory_exists(tmp_dir)
        crop_box = (231, 134, 748, 449)
        cropped_output_path = os.path.join(
            tmp_dir, f"{identifier}_cropped_image_blue.png"
        )

        print(f"DEBUG: About to crop image to: {cropped_output_path}")
        crop_image(image_path, crop_box, output_path=cropped_output_path)

        # Verify the cropped file was created
        if not os.path.exists(cropped_output_path):
            raise FileNotFoundError(
                f"Cropped image was not created: {cropped_output_path}"
            )

        background_colors = [
            (193, 206, 228),
            (216, 224, 199),
            (188, 202, 161),
            (0, 0, 0),
            (255, 255, 255),
            (45, 34, 14),
            (154, 143, 141),
            (255, 246, 216),
            (28, 47, 64),
            (215, 234, 230),
            (167, 190, 217),
            (185, 224, 255),
            (133, 195, 246),
            (122, 123, 118),
        ]

        print("DEBUG: About to remove background colors")
        remove_background_colors(cropped_output_path, background_colors, tolerance=35)

        print("DEBUG: About to convert to pure blue")
        convert_to_pure_blue(cropped_output_path, output_path=output_path)

        print("DEBUG: create_blue_graph completed successfully")

    except Exception as e:
        print(f"ERROR in create_blue_graph: {e}")
        raise


def overlay_images(background_path, overlay_path, output_path, position=(0, 0)):
    try:
        # Check if input files exist
        if not os.path.exists(background_path):
            raise FileNotFoundError(f"Background image not found: {background_path}")
        if not os.path.exists(overlay_path):
            raise FileNotFoundError(f"Overlay image not found: {overlay_path}")

        background = Image.open(background_path).convert("RGBA")
        overlay = Image.open(overlay_path).convert("RGBA")

        background.paste(overlay, position, overlay)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        background.save(output_path)
        print(f"DEBUG: Images overlaid successfully, saved to: {output_path}")

    except Exception as e:
        print(f"ERROR in overlay_images: {e}")
        raise


def ensure_directory_exists(directory_path):
    """Ensure that a directory exists; if not, create it."""
    try:
        os.makedirs(directory_path, exist_ok=True)
        print(f"DEBUG: Directory ensured: {directory_path}")
    except Exception as e:
        print(f"ERROR creating directory {directory_path}: {e}")
        raise


def resize_image(image_path, output_path, scale_factor=2, preserve_colors=False):
    """
    Resize an image by a given scale factor while optionally preserving the original red and blue color values
    and maintaining the organic, wavy look.

    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the resized image.
        scale_factor (float): Factor by which to scale the image.
        preserve_colors (bool): Whether to preserve the original red and blue color values. Default is False.
    """
    try:
        # Check if input file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Input image not found: {image_path}")

        # Load the image
        img = Image.open(image_path).convert("RGBA")
        width, height = img.size
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)

        # Resize using nearest neighbor to maintain sharp edges
        resized_img = img.resize((new_width, new_height), Image.NEAREST)

        if not preserve_colors:
            # Convert to numpy array for pixel manipulation
            data = np.array(resized_img)

            # Extract RGB channels
            r, g, b, a = data.T

            # Create masks for red-dominant and blue-dominant pixels
            red_dominant = (r > g) & (r > b) & (a > 0)
            blue_dominant = (b > r) & (b > g) & (a > 0)

            # Set all non-red-dominant, non-blue-dominant pixels to transparent
            transparent_mask = ~(red_dominant | blue_dominant)
            data[..., 3][
                transparent_mask.T
            ] = 0  # Set alpha to 0 for transparent pixels

            # For red-dominant pixels, preserve the red value but zero out green and blue
            data[..., 1][red_dominant.T] = 0
            data[..., 2][red_dominant.T] = 0

            # For blue-dominant pixels, preserve the blue value but zero out red and green
            data[..., 0][blue_dominant.T] = 0
            data[..., 1][blue_dominant.T] = 0

            # Convert back to image
            result_img = Image.fromarray(data)
        else:
            result_img = resized_img

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save the result
        result_img.save(output_path)
        print(f"DEBUG: Image resized successfully, saved to: {output_path}")

    except Exception as e:
        print(f"ERROR in resize_image: {e}")
        raise


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
    try:
        print("DEBUG: Starting create_dual_facet_graphs")
        print(f"  First PDF: {first_pdf_path}")
        print(f"  Second PDF: {second_pdf_path}")
        print(f"  Output dir: {output_dir}")

        # Extract the first 6 letters of each file name for identifier
        first_name_part = sanitize_path_component(os.path.basename(first_pdf_path)[:6])
        first_name = sanitize_filename(
            os.path.basename(first_pdf_path).replace(".pdf", "")
        )
        second_name_part = sanitize_path_component(
            os.path.basename(second_pdf_path)[:6]
        )
        second_name = sanitize_filename(
            os.path.basename(second_pdf_path).replace(".pdf", "")
        )
        identifier = f"{first_name_part}_{second_name_part}"

        print(f"DEBUG: Using identifier: {identifier}")

        # Set up directories
        if output_dir is None:
            output_dir = r"F:\projects\MBTInfo\backend\media\tmp"

        tmp_dir = output_dir
        final_dir = os.path.join(tmp_dir, "final")
        ensure_directory_exists(tmp_dir)
        ensure_directory_exists(final_dir)

        print(f"DEBUG: Extracting graphs from {first_name_part}'s PDF...")
        first_pdf_output_dir = os.path.join(output_dir, first_name)
        extract_all_facet_graphs(first_pdf_path, output_dir)

        print(f"DEBUG: Extracting graphs from {second_name_part}'s PDF...")
        second_pdf_output_dir = os.path.join(output_dir, second_name)
        extract_all_facet_graphs(second_pdf_path, output_dir)

        # List of graph types to process
        graph_types = ["EIGraph", "SNgraph", "TFgraph", "JPgraph"]

        # Dictionary to store output paths
        output_paths = {}

        # Process each graph type
        for graph_type in graph_types:
            print(f"DEBUG: Processing {graph_type}...")

            # Define background image path based on graph type
            background_path = rf"F:\projects\MBTInfo\backend\media\Dual_Report_Media\backgrounds\background{graph_type[:2]}.jpeg"

            # Define paths for first and second PDFs' graphs
            page_num = (
                5
                if graph_type == "EIGraph"
                else (
                    6
                    if graph_type == "SNgraph"
                    else 7 if graph_type == "TFgraph" else 8
                )
            )

            first_graph_path = os.path.join(
                first_pdf_output_dir, "screenshots", f"page{page_num}_{graph_type}.png"
            )
            second_graph_path = os.path.join(
                second_pdf_output_dir, "screenshots", f"page{page_num}_{graph_type}.png"
            )

            print("DEBUG: Looking for graph files:")
            print(
                f"  First: {first_graph_path} (exists: {os.path.exists(first_graph_path)})"
            )
            print(
                f"  Second: {second_graph_path} (exists: {os.path.exists(second_graph_path)})"
            )

            # Check if the required graph files exist
            if not os.path.exists(first_graph_path):
                print(f"WARNING: First graph not found: {first_graph_path}")
                continue
            if not os.path.exists(second_graph_path):
                print(f"WARNING: Second graph not found: {second_graph_path}")
                continue

            # Create red and blue graphs with initial processing
            red_output_path = os.path.join(
                tmp_dir, f"{identifier}_{graph_type}_red.png"
            )
            blue_output_path = os.path.join(
                tmp_dir, f"{identifier}_{graph_type}_blue.png"
            )

            create_red_graph(
                first_graph_path, output_path=red_output_path, identifier=identifier
            )
            create_blue_graph(
                second_graph_path, output_path=blue_output_path, identifier=identifier
            )

            # Resize the images
            resized_red_path = os.path.join(
                tmp_dir, f"{identifier}_{graph_type}_red_resized.png"
            )
            resized_blue_path = os.path.join(
                tmp_dir, f"{identifier}_{graph_type}_blue_resized.png"
            )

            resize_image(red_output_path, resized_red_path, scale_factor=1.66)
            resize_image(blue_output_path, resized_blue_path, scale_factor=1.66)

            # Combine the enhanced graphs
            combined_path = os.path.join(
                tmp_dir, f"{identifier}_{graph_type}_combined.png"
            )
            overlay_images(
                resized_blue_path, resized_red_path, combined_path, position=(0, 9)
            )

            # Create final output with background
            final_output_path = os.path.join(
                final_dir, f"{identifier}_{graph_type}_final.png"
            )
            overlay_images(
                background_path, combined_path, final_output_path, position=(375, 170)
            )

            # Store the output path
            output_paths[graph_type] = final_output_path

            print(f"DEBUG: Completed {graph_type} graph")

        print("DEBUG: All graphs created successfully!")
        return output_paths

    except Exception as e:
        print(f"ERROR in create_dual_facet_graphs: {e}")
        raise


def create_first_graph(first_pdf_path, second_pdf_path, output_dir):
    try:
        first_name_part = sanitize_path_component(os.path.basename(first_pdf_path)[:6])
        second_name_part = sanitize_path_component(
            os.path.basename(second_pdf_path)[:6]
        )
        identifier = f"{first_name_part}_{second_name_part}"
        background_path = r"F:\projects\MBTInfo\backend\media\Dual_Report_Media\backgrounds\backgroundMBTI.jpeg"

        # Set up directories
        if output_dir is None:
            output_dir = r"F:\projects\MBTInfo\backend\media\tmp"

        tmp_dir = output_dir
        final_dir = os.path.join(tmp_dir, "final")
        ensure_directory_exists(tmp_dir)
        ensure_directory_exists(final_dir)

        print(f"DEBUG: Extracting graph from {first_name_part}'s PDF...")
        print(f"DEBUG: Extracting graph from {second_name_part}'s PDF...")
        target_colors = [
            (192, 208, 167),
            (206, 218, 187),
            (178, 197, 148),
            (164, 187, 129),
            (0, 0, 0),
            (255, 255, 255),
            (126, 124, 124),
        ]
        first_graph_one_path = extract_first_graph(first_pdf_path, tmp_dir)
        first_graph_two_path = extract_first_graph(second_pdf_path, tmp_dir)

        # Check if extraction was successful
        if not os.path.exists(first_graph_one_path):
            raise FileNotFoundError(
                f"First graph extraction failed: {first_graph_one_path}"
            )
        if not os.path.exists(first_graph_two_path):
            raise FileNotFoundError(
                f"Second graph extraction failed: {first_graph_two_path}"
            )

        remove_background_colors(first_graph_one_path, target_colors, tolerance=60)
        remove_background_colors(first_graph_two_path, target_colors, tolerance=60)

        convert_blue_to_red(first_graph_one_path, rf"{tmp_dir}\first_graph_one_red.png")
        convert_to_pure_blue(
            first_graph_two_path, rf"{tmp_dir}\first_graph_two_blue.png"
        )

        resized_red_path = os.path.join(tmp_dir, f"{identifier}_one_red_resized.png")
        resized_blue_path = os.path.join(tmp_dir, f"{identifier}_two_blue_resized.png")

        resize_image(
            rf"{tmp_dir}\first_graph_one_red.png", resized_red_path, scale_factor=1.4
        )
        resize_image(
            rf"{tmp_dir}\first_graph_two_blue.png", resized_blue_path, scale_factor=1.4
        )

        overlay_images(
            resized_blue_path,
            resized_red_path,
            rf"{tmp_dir}\first_graph_combined.png",
            position=(0, 12),
        )
        overlay_images(
            background_path,
            rf"{tmp_dir}\first_graph_combined.png",
            rf"{final_dir}\{identifier}_first_graph_final.png",
            position=(328, 106),
        )
        return rf"{final_dir}\{identifier}_first_graph_final.png"

    except Exception as e:
        print(f"ERROR in create_first_graph: {e}")
        raise


def create_dominant_graph(first_pdf_path, second_pdf_path, output_dir):
    try:
        first_name_part = sanitize_path_component(os.path.basename(first_pdf_path)[:6])
        second_name_part = sanitize_path_component(
            os.path.basename(second_pdf_path)[:6]
        )
        identifier = f"{first_name_part}_{second_name_part}"
        background_path = r"F:\projects\MBTInfo\backend\media\Dual_Report_Media\backgrounds\white_1180x480.png"
        text_path = r"F:\projects\MBTInfo\backend\media\Dual_Report_Media\backgrounds\backgroundtext.png"

        # Set up directories
        if output_dir is None:
            output_dir = r"F:\projects\MBTInfo\backend\media\tmp"

        tmp_dir = output_dir
        final_dir = os.path.join(tmp_dir, "final")
        ensure_directory_exists(tmp_dir)
        ensure_directory_exists(final_dir)

        print(f"DEBUG: Extracting graph from {first_name_part}'s PDF...")
        print(f"DEBUG: Extracting graph from {second_name_part}'s PDF...")
        dom_graph_one_path = extract_dominant_graph(first_pdf_path, tmp_dir)
        dom_graph_two_path = extract_dominant_graph(second_pdf_path, tmp_dir)

        # Check if extraction was successful
        if not os.path.exists(dom_graph_one_path):
            raise FileNotFoundError(
                f"First dominant graph extraction failed: {dom_graph_one_path}"
            )
        if not os.path.exists(dom_graph_two_path):
            raise FileNotFoundError(
                f"Second dominant graph extraction failed: {dom_graph_two_path}"
            )

        target_colors = [(226, 234, 215)]
        remove_background_colors(dom_graph_one_path, target_colors, tolerance=60)
        remove_background_colors(dom_graph_two_path, target_colors, tolerance=60)
        overlay_images(
            background_path,
            dom_graph_one_path,
            rf"{tmp_dir}\dominant_graph_combined.png",
            position=(90, 140),
        )
        overlay_images(
            rf"{tmp_dir}\dominant_graph_combined.png",
            dom_graph_two_path,
            rf"{final_dir}\{identifier}_dominant_graph_final.png",
            position=(634, 140),
        )
        overlay_images(
            rf"{final_dir}\{identifier}_dominant_graph_final.png",
            text_path,
            rf"{final_dir}\{identifier}_dominant_final_final.png",
            position=(84, 36),
        )
        print(f"DEBUG: Creating final image for {identifier}'s dominant graph...")
        return rf"{final_dir}\{identifier}_dominant_graph_final.png"

    except Exception as e:
        print(f"ERROR in create_dominant_graph: {e}")
        raise


def create_all_graphs(first_pdf_path, second_pdf_path, output_dir):
    try:
        print("DEBUG: Starting create_all_graphs")
        facet_graphs = create_dual_facet_graphs(
            first_pdf_path, second_pdf_path, output_dir
        )
        first_graph = create_first_graph(first_pdf_path, second_pdf_path, output_dir)
        dominant_graph = create_dominant_graph(
            first_pdf_path, second_pdf_path, output_dir
        )
        print(f"All graphs created successfully! at:\n{output_dir}\\final")
        print(f"{facet_graphs}\n{first_graph}\n{dominant_graph}")
        return

    except Exception as e:
        print(f"ERROR in create_all_graphs: {e}")
        raise


if __name__ == "__main__":
    first_pdf_path = r"F:\projects\MBTInfo\input\Eran-Amiry-267149-743ec182-78a1-ee11-8925-000d3a36c80e.pdf"
    second_pdf_path = r"F:\projects\MBTInfo\input\Benyamin-Meiri-267149-b4eb8524-3773-ef11-bdfd-000d3a58cdb7.pdf"

    # Extract identifier based on both filenames
    first_name_part = sanitize_path_component(
        os.path.basename(first_pdf_path).replace(".pdf", "")[:6]
    )
    second_name_part = sanitize_path_component(
        os.path.basename(second_pdf_path).replace(".pdf", "")[:6]
    )
    identifier = f"{first_name_part}_{second_name_part}"

    # Set unified output directory
    output_dir = os.path.join(r"F:\projects\MBTInfo\backend\media\tmp", identifier)

    # Run full graph generation
    create_all_graphs(first_pdf_path, second_pdf_path, output_dir)
