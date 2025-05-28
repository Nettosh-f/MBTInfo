import fitz  # PyMuPDF
import os
import time
import re


def extract_graph_from_pdf(pdf_path, output_image_path, page_num=4, rect_coords=None, zoom=2):
    """
    Extract a graph or image from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file
        output_image_path (str): Path where the extracted image will be saved
        page_num (int): Page number (0-based index)
        rect_coords (tuple): Optional tuple of (x0, y0, x1, y1) as percentages of page dimensions
                            Default is (0.1, 0.12, 0.9, 0.44) if None
        zoom (int): Zoom factor for better quality
    """
    # Open the PDF
    pdf_document = fitz.open(pdf_path)

    # Get the specified page
    page = pdf_document[page_num]

    # Get page dimensions
    page_rect = page.rect

    # Use default rectangle coordinates if none provided
    if rect_coords is None:
        rect_coords = (0.1, 0.12, 0.9, 0.44)  # Default values

    # Unpack the rectangle coordinates (as percentages of page dimensions)
    x0_pct, y0_pct, x1_pct, y1_pct = rect_coords

    # Calculate actual coordinates
    x0 = page_rect.width * x0_pct
    y0 = page_rect.height * y0_pct
    x1 = page_rect.width * x1_pct
    y1 = page_rect.height * y1_pct

    graph_rect = fitz.Rect(x0, y0, x1, y1)

    # Create a pixmap from the defined rectangle
    pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=graph_rect)

    # Save the pixmap as an image
    pixmap.save(output_image_path)

    pdf_document.close()

    print(f"Graph extracted and saved to {output_image_path}")


def extract_multiple_graphs_from_pdf(pdf_path, output_dir, page_num, rect_coords_dict, zoom=2):
    """
    Extract multiple graphs or images from a single PDF page.

    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Directory where extracted images will be saved
        page_num (int): Page number (0-based index)
        rect_coords_dict (dict): Dictionary with name indicators as keys and coordinate tuples as values
        zoom (int): Zoom factor for better quality
    """
    # Open the PDF
    pdf_document = fitz.open(pdf_path)

    # Get the specified page
    page = pdf_document[page_num]

    # Get page dimensions
    page_rect = page.rect

    # Create a specific output directory based on PDF filename
    pdf_filename = os.path.basename(pdf_path)
    pdf_name_without_ext = os.path.splitext(pdf_filename)[0]
    specific_output_dir = os.path.join(output_dir, pdf_name_without_ext, "screenshots")
    os.makedirs(specific_output_dir, exist_ok=True)

    # Create a dictionary to track filenames used in this run
    if not hasattr(extract_multiple_graphs_from_pdf, 'used_filenames'):
        extract_multiple_graphs_from_pdf.used_filenames = set()

    # Extract each graph based on provided coordinates
    for name_indicator, rect_coords in rect_coords_dict.items():
        # Unpack the rectangle coordinates (as percentages of page dimensions)
        x0_pct, y0_pct, x1_pct, y1_pct = rect_coords

        # Calculate actual coordinates
        x0 = page_rect.width * x0_pct
        y0 = page_rect.height * y0_pct
        x1 = page_rect.width * x1_pct
        y1 = page_rect.height * y1_pct

        graph_rect = fitz.Rect(x0, y0, x1, y1)

        # Create a pixmap from the defined rectangle
        pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=graph_rect)

        # Create output filename using the name indicator
        base_filename = f"page{page_num + 1}_{name_indicator}.png"
        output_image_path = os.path.join(specific_output_dir, base_filename)

        # Check if this filename has been used in this run
        while output_image_path in extract_multiple_graphs_from_pdf.used_filenames:
            # If it has, create a unique filename for this run
            name, ext = os.path.splitext(base_filename)
            base_filename = f"{name}_duplicate{ext}"
            output_image_path = os.path.join(specific_output_dir, base_filename)

        # Add to used filenames
        extract_multiple_graphs_from_pdf.used_filenames.add(output_image_path)

        # Save the pixmap as an image
        pixmap.save(output_image_path)

        print(f"Graph '{name_indicator}' extracted from page {page_num + 1} and saved to {output_image_path}")

    pdf_document.close()

if __name__ == "__main__":
    # Path to your PDF file
    pdf_path = r"F:\projects\MBTInfo\input\Tomer Shimon-Haiman-267149-7381d4d8-6235-f011-8b3d-000d3a381fe7.pdf"

    # Output image path
    output_dir = r"F:\projects\MBTInfo\output"
    os.makedirs(output_dir, exist_ok=True)

    # Reset the used filenames for this run
    extract_multiple_graphs_from_pdf.used_filenames = set()

    # Define different rectangle coordinates for each page with name indicators
    # Format: Dictionary with name indicators as keys and coordinate tuples as values
    page_rectangles = {
        4: {
            "EIGraph": (0.1, 0.12, 0.9, 0.44),

        },
        5: {
            "SNgraph": (0.1, 0.12, 0.9, 0.44),

        },
        6: {
            "TFgraph": (0.1, 0.12, 0.9, 0.44),

        },
        7: {
            "JPgraph": (0.1, 0.12, 0.9, 0.44),

        }
    }

    pages_list = [4,5,6,7]
    # page_rectangles = {0: {
    #         "ST": (0.71, 0.54, 0.9, 0.76),
    #
    #     }}
    # pages_list = [0]
    for page_num in pages_list:
        print(f"Extracting graphs from page {page_num + 1}")
        rect_coords_dict = page_rectangles.get(page_num)
        extract_multiple_graphs_from_pdf(
            pdf_path,
            output_dir,
            page_num,
            rect_coords_dict,
            zoom=2
        )