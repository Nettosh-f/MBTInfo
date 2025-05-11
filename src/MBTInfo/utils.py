import re
import os
from datetime import datetime
from consts import MBTI_TYPES, FACETS, MIDZONE_FACETS
from typing import Dict, Optional, List, Tuple


def parse_mbti_scores(line: str) -> dict:

    # Use regex to find all pairs of MBTI dimension and score
    pairs = re.findall(r'(\w+)\s+\|\s+(\d+)', line)

    # Create a dictionary from the pairs, converting scores to integers
    return {dimension.lower(): int(score) for dimension, score in pairs}


def find_and_parse_mbti_scores(file_path: str) -> dict:

    pattern = r'\b(EXTRAVERSION|INTUITION|THINKING|PERCEIVING)\s+\|\s+\d+'

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if re.search(pattern, line):
                    return parse_mbti_scores(line)
    except IOError as e:
        print(f"Error reading file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return {}  # Return empty dictionary if no matching line is found or if there's an error


def find_type(file_path: str) -> Optional[str]:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    for mbti_type in MBTI_TYPES:
        if mbti_type in content:
            return mbti_type
    return None


def get_name(file_path: str) -> Optional[str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Skip the first 9 lines
            for _ in range(8):
                next(file, None)
            
            # Read the 10th line
            tenth_line = next(file, '').strip()
            return tenth_line if tenth_line else None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


def get_date(file_path: str) -> Optional[str]:

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Skip the first 10 lines
            for _ in range(9):
                next(file, None)
            
            # Read the 11th line
            eleventh_line = next(file, '').strip()
            return eleventh_line if eleventh_line else None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


def get_all_info(file_path: str) -> Dict[str, Optional[str]]:
    info = {
        'name': get_name(file_path),
        'date': get_date(file_path),
        'type': find_type(file_path)
    }
    return info


def convert_scores_to_mbti_dict(scores: Dict[str, int]) -> Dict[str, int]:
    """
    Convert a dictionary of MBTI scores to a dictionary with MBTI letters as keys.

    Args:
    scores (Dict[str, int]): A dictionary with MBTI dimensions as keys and scores as values.

    Returns:
    Dict[str, int]: A dictionary with MBTI letters as keys and scores as values.
    """
    mbti_dict = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}

    for dimension, score in scores.items():
        if dimension == 'extraversion':
            mbti_dict['E'] = score
        elif dimension == 'introversion':
            mbti_dict['I'] = score
        elif dimension == 'sensing':
            mbti_dict['S'] = score
        elif dimension == 'intuition':
            mbti_dict['N'] = score
        elif dimension == 'thinking':
            mbti_dict['T'] = score
        elif dimension == 'feeling':
            mbti_dict['F'] = score
        elif dimension == 'judging':
            mbti_dict['J'] = score
        elif dimension == 'perceiving':
            mbti_dict['P'] = score

    return mbti_dict


def get_input_files(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.pdf')]


def create_output_directory():
    base_dir = r"F:\projects\MBTInfo\output"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def collect_preferred_qualities(file_path: str) -> List[str]:
    preferred_qualities = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        for i, line in enumerate(lines):
            if 'in-preference' in line.lower():
                if i > 0:
                    # Get the previous line and split it into words
                    prev_line = lines[i-1].strip()
                    words = prev_line.split()
                    if words:
                        # Add the last word from the previous line
                        preferred_qualities.append(words[-1])
        words_to_remove = {'and', 'I', '|5', '|6', 'harmony', 'spontaneity', 'pole.', 'to', 'your'}
        filtered_qualities = [quality for quality in preferred_qualities if quality.lower() not in words_to_remove]
        filtered_qualities.pop(0)


        preferred_qualities = filtered_qualities

        print(f"Found {len(preferred_qualities)} preferred qualities.")
    except Exception as e:
        print(f"An error occurred while processing {file_path}: {str(e)}")

    return preferred_qualities


def collect_midzone_qualities(file_path: str) -> List[str]:
    midzone_qualities = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        for i, line in enumerate(lines):
            if 'midzone' in line.lower():
                if i > 0:
                    # Get the previous line and split it into words
                    prev_line = lines[i-1].strip()
                    words = prev_line.split()
                    if words:
                        # Add the last word from the previous line
                        midzone_qualities.append(words[-1])
        words_to_remove = {'and', 'would', '|5', '|6', 'cause-and-eﬀect,', 'the', 'with', 'facets.', 'distractions.',
                           'preference', 'many'}
        filtered_qualities = [quality for quality in midzone_qualities if quality.lower() not in words_to_remove]
        filtered_qualities.pop(0)

        # Split qualities based on "-" and flatten the list
        split_qualities = [item.strip() for quality in filtered_qualities for item in quality.split('–')]
        # Remove duplicates while preserving order, case-insensitive
        seen = set()
        midzone_qualities = []
        for quality in split_qualities:
            lower_quality = quality.lower()
            if lower_quality not in seen:
                seen.add(lower_quality)
                midzone_qualities.append(quality)

        print(f"Found {len(midzone_qualities)} midzone qualities.")
    except Exception as e:
        print(f"An error occurred while processing {file_path}: {str(e)}")

    return midzone_qualities


def collect_out_qualities(file_path: str) -> List[str]:
    out_qualities = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        for i, line in enumerate(lines):
            if 'out-of-preference' in line.lower():
                if i > 0:
                    # Get the previous line and split it into words
                    prev_line = lines[i-1].strip()
                    words = prev_line.split()
                    if words:
                        # Add the last word from the previous line
                        out_qualities.append(words[-1])
        words_to_remove = {'and', '|5', '|6', 'use.', 'spontaneity', 'preference'}
        filtered_qualities = [quality for quality in out_qualities if quality.lower() not in words_to_remove]
        filtered_qualities.pop(0)

        # Remove duplicates while preserving order
        out_qualities = list(dict.fromkeys(filtered_qualities))

        print(f"Found {len(out_qualities)} out of preference qualities.")
    except Exception as e:
        print(f"An error occurred while processing {file_path}: {str(e)}")

    return out_qualities


def collect_qualities(file_path: str) -> Tuple[List[str], List[str], List[str]]:
    preferred_qualities = collect_preferred_qualities(file_path)
    midzone_qualities = collect_midzone_qualities(file_path)
    out_qualities = collect_out_qualities(file_path)
    return preferred_qualities, midzone_qualities, out_qualities


def check_communication(file_path: str) -> list[str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            start_marker = "YOUR FACET RESULT COMMUNICATION STYLE ENHANCING YOUR STYLE"
            end_marker = "|10"
            communication_facets = []
            
            start_index = content.find(start_marker)
            end_index = content.find(end_marker, start_index)
            
            if start_index != -1 and end_index != -1:
                communication_content = content[start_index + len(start_marker):end_index]
                lines = communication_content.split('\n')
                facets_lower = [facet.lower() for facet in FACETS]
                midzone_lower = [facet.lower() for facet in MIDZONE_FACETS]
                for line in lines:
                    words = line.strip().split()
                    if words and words[0].lower() in (facets_lower + midzone_lower):
                        communication_facets.append(words[0].lower())

            filtered_facets = []
            for facet in communication_facets:
                if not any(facet in other_facet and facet != other_facet for other_facet in communication_facets):
                    filtered_facets.append(facet)
            
            return filtered_facets
    except Exception as e:
        print(f"An error occurred while processing {file_path}: {str(e)}")
        return []


def check_managing_conflict(file_path: str) -> list[str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            start_marker = "YOUR FACET RESULT CONFLICT MANAGEMENT STYLE ENHANCING YOUR STYLE"
            end_marker = "|13"
            decision_facets = []
            
            start_index = content.find(start_marker)
            end_index = content.find(end_marker, start_index)
            
            if start_index != -1 and end_index != -1:
                decision_content = content[start_index + len(start_marker):end_index]
                lines = decision_content.split('\n')
                facets_lower = [facet.lower() for facet in FACETS]
                midzone_lower = [facet.lower() for facet in MIDZONE_FACETS]
                for line in lines:
                    words = line.strip().split()
                    if words and words[0].lower() in (facets_lower + midzone_lower):
                        decision_facets.append(words[0].lower())

            filtered_facets = []
            for facet in decision_facets:
                if not any(facet in other_facet and facet != other_facet for other_facet in decision_facets):
                    filtered_facets.append(facet)
            
            return filtered_facets
    except Exception as e:
        print(f"An error occurred while processing {file_path}: {str(e)}")
        return []


def check_managing_change(file_path: str) -> list[str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            start_marker = "YOUR FACET RESULT CHANGE MANAGEMENT STYLE ENHANCING YOUR STYLE"
            end_marker = "|12"
            change_facets = []
            
            start_index = content.find(start_marker)
            end_index = content.find(end_marker, start_index)
            
            if start_index != -1 and end_index != -1:
                change_content = content[start_index + len(start_marker):end_index]
                lines = change_content.split('\n')
                facets_lower = [facet.lower() for facet in FACETS]
                midzone_lower = [facet.lower() for facet in MIDZONE_FACETS]
                for line in lines:
                    words = line.strip().split()
                    if words and words[0].lower() in (facets_lower + midzone_lower):
                        change_facets.append(words[0].lower())

            filtered_facets = []
            for facet in change_facets:
                if not any(facet in other_facet and facet != other_facet for other_facet in change_facets):
                    filtered_facets.append(facet)
            
            return filtered_facets
    except Exception as e:
        print(f"An error occurred while processing {file_path}: {str(e)}")
        return []


def reorder_sheets(workbook):
    """Reorder sheets to put Dashboard first, followed by main data sheet"""
    # Get the current sheet names
    sheet_names = workbook.sheetnames

    # Define the desired order - Dashboard first, then Data, then others
    desired_order = []

    # Add Dashboard if it exists
    if 'Dashboard' in sheet_names:
        desired_order.append('Dashboard')

    # Add Data if it exists
    if 'Data' in sheet_names:
        desired_order.append('Data')

    # Add any other sheets in their original order
    for sheet_name in sheet_names:
        if sheet_name not in desired_order:
            desired_order.append(sheet_name)

    # Reorder the sheets
    workbook._sheets = [workbook[sheet_name] for sheet_name in desired_order]


if __name__ == "__main__":
    test_file_path = r"F:\projects\MBTInfo\textfiles\ADAM-POMERANTZ-267149-e4b6edb5-1a5f-ef11-bdfd-6045bd04b01a_text.txt"
    directory = r"F:\projects\MBTInfo\output"
    print(get_all_info(test_file_path))
    print(check_communication(test_file_path))
    print(check_managing_change(test_file_path))
    print(check_managing_conflict(test_file_path))