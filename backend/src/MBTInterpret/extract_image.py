import fitz  # PyMuPDF
import os
import time
import re
from utilsAI import get_mbti_type_from_pdf


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
    specific_output_dir = output_dir
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
        base_filename = f"{pdf_name_without_ext[:6]}_{name_indicator}.png"
        output_image_path = os.path.join(specific_output_dir, base_filename)

        # Check if this filename has been used in this run
        while output_image_path in extract_multiple_graphs_from_pdf.used_filenames:
            # If it has, create a unique filename for this run
            name, ext = os.path.splitext(base_filename)
            base_filename = f"{name}_duplicate{ext}"
            output_image_path = specific_output_dir

        # Add to used filenames
        extract_multiple_graphs_from_pdf.used_filenames.add(output_image_path)

        # Save the pixmap as an image
        pixmap.save(output_image_path)

        # print(f"Graph '{name_indicator}' extracted from page {page_num + 1} and saved to {output_image_path}")

    pdf_document.close()


def extract_all_facet_graphs(pdf_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    extract_multiple_graphs_from_pdf.used_filenames = set()
    page_rectangles = {
        4: {"EIGraph": (0.1, 0.12, 0.9, 0.44)},
        5: {"SNgraph": (0.1, 0.12, 0.9, 0.44)},
        6: {"TFgraph": (0.1, 0.12, 0.9, 0.44)},
        7: {"JPgraph": (0.1, 0.12, 0.9, 0.44)}}
    pages_list = [4, 5, 6, 7]
    for page_num in pages_list:
        # print(f"Extracting graphs from page {page_num + 1}")
        rect_coords_dict = page_rectangles.get(page_num)
        extract_multiple_graphs_from_pdf(
            pdf_path,
            output_dir,
            page_num,
            rect_coords_dict,
            zoom=2
        )


def extract_first_graph(pdf_path, output_dir):
    """
    Extract the first graph from a PDF and save it as an image.

    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Directory where the extracted image will be saved
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    if get_mbti_type_from_pdf(pdf_path) == "ISTJ":
        # Define the rectangle coordinates for the first graph
        rect_coords = (0.248, 0.6475, 0.748, 0.766)  # Example coordinates
        print("type is ISTJ")
    else:
        # Define the rectangle coordinates for the first graph
        rect_coords = (0.248, 0.66665, 0.748, 0.7845)  # Example coordinates

    # Define the output image path
    pdf_filename = os.path.basename(pdf_path)
    pdf_name_without_ext = os.path.splitext(pdf_filename)[0]
    output_image_path = os.path.join(output_dir, f"{pdf_name_without_ext[:6]}_first_graph.png")

    # Extract the graph from the PDF
    extract_graph_from_pdf(pdf_path, output_image_path, page_num=2, rect_coords=rect_coords, zoom=2)

    # print(f"First graph extracted and saved to {output_image_path}")

    return output_image_path


def extract_dominant_graph(pdf_path, output_dir):
    """
    Extract the dominant graph from a PDF and save it as an image.

    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Directory where the extracted image will be saved
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define the rectangle coordinates for the first graph
    rect_coords = (0.31, 0.28, 0.68, 0.455)  # Example coordinates

    # Define the output image path
    pdf_filename = os.path.basename(pdf_path)
    pdf_name_without_ext = os.path.splitext(pdf_filename)[0]
    output_image_path = os.path.join(output_dir, f"{pdf_name_without_ext[:6]}_dominant_graph.png")

    # Extract the graph from the PDF
    extract_graph_from_pdf(pdf_path, output_image_path, page_num=12, rect_coords=rect_coords, zoom=2)

    # print(f"First graph extracted and saved to {output_image_path}")

    return output_image_path


def extract_last_graph(pdf_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Define the rectangle coordinates for the first graph
    rect_coords = (0.31, 0.28, 0.68, 0.455)  # Example coordinates

    # Define the output image path
    pdf_filename = os.path.basename(pdf_path)
    pdf_name_without_ext = os.path.splitext(pdf_filename)[0]
    output_image_path = os.path.join(output_dir, f"{pdf_name_without_ext[:6]}_step_II_results_graph.png")

    # Extract the graph from the PDF
    extract_graph_from_pdf(pdf_path, output_image_path, page_num=15, rect_coords=rect_coords, zoom=2)

    # print(f"First graph extracted and saved to {output_image_path}")

    return output_image_path

if __name__ == "__main__":
    path_to_pdf = r"F:\projects\MBTInfo\input\Eran-Amiry-267149-743ec182-78a1-ee11-8925-000d3a36c80e.pdf"
    name = os.path.basename(path_to_pdf).replace('.pdf', '')[:6]
    path_to_output_dir = os.path.join(r"F:\projects\MBTInfo\backend\media\tmp", name)

    extract_first_graph(path_to_pdf, path_to_output_dir)
    extract_dominant_graph(path_to_pdf, path_to_output_dir)
    extract_all_facet_graphs(path_to_pdf, path_to_output_dir)
    extract_last_graph(path_to_pdf, path_to_output_dir)
    # extract_dominant_graph(path_to_pdf, path_to_output_dir)