import fitz  # PyMuPDF
import os


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
    pdf_path = r"F:\projects\MBTInfo\input\ADAM-POMERANTZ-267149-e4b6edb5-1a5f-ef11-bdfd-6045bd04b01a.pdf"

    # Output image path
    output_dir = r"F:\projects\MBTInfo\output"
    os.makedirs(output_dir, exist_ok=True)

    # Reset the used filenames for this run
    extract_multiple_graphs_from_pdf.used_filenames = set()

    # Define different rectangle coordinates for each page with name indicators
    # Format: Dictionary with name indicators as keys and coordinate tuples as values
    page_rectangles = {
        4: {
            "ExtIntGraph": (0.1, 0.12, 0.9, 0.44),
            "Initiating-Receiving": (0.088, 0.45, 0.9, 0.534),
            "Expressive-Contained": (0.088, 0.534, 0.9, 0.615),
            "Gregarious-Intimate": (0.088, 0.615, 0.9, 0.7),
            "Active-Reflactive": (0.088, 0.7, 0.9, 0.785),
            "Enthusiastic-Quite": (0.088, 0.785, 0.9, 0.865),
        },
        5: {
            "facet_scores_1": (0.1, 0.12, 0.9, 0.44),
            "Concrete–Abstract": (0.088, 0.45, 0.9, 0.54),
            "Realistic–Imaginative": (0.088, 0.54, 0.9, 0.62),
            "Practical–Conceptual": (0.088, 0.62, 0.9, 0.69),
            "Experiential–Theoretical": (0.088, 0.69, 0.9, 0.775),
            "Traditional–Original": (0.088, 0.775, 0.9, 0.875),
        },
        6: {
            "type_dynamics": (0.1, 0.12, 0.9, 0.44),
            "Logical–Empathetic": (0.088, 0.445, 0.9, 0.53),
            "Reasonable–Compassionate": (0.088, 0.528, 0.9, 0.6),
            "Questioning–Accommodating": (0.088, 0.6, 0.9, 0.685),
            "Critical–Accepting": (0.088, 0.7, 0.9, 0.785),
            "Tough–Tender": (0.088, 0.785, 0.9, 0.865),
        },
        7: {
            "type_comparison": (0.1, 0.12, 0.9, 0.44),
            "Systematic–Casual": (0.088, 0.45, 0.9, 0.534),
            "Planful–OpenEnded": (0.088, 0.534, 0.9, 0.615),
            "EarlyStarting–PressurePrompted": (0.088, 0.615, 0.9, 0.7),
            "Scheduled–Spontaneous": (0.088, 0.7, 0.9, 0.785),
            "Methodical–Emergent": (0.088, 0.785, 0.9, 0.865),
        }
    }
    pages_list = [4, 5, 6, 7]
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