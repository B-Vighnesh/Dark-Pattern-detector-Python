#Till here it analyses desktop screen and tell whether the data in dataset is present or not 
from PIL import Image
import pytesseract
import re
import mss
import pygetwindow as gw  # To target specific windows
import numpy as np
import time

# Uncomment and update the Tesseract-OCR path if it's not in your system's PATH
# pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

def normalize_text(text):
    """Normalize text by removing extra whitespace and ensuring lowercase."""
    return re.sub(r'\s+', ' ', text.strip().lower())

def extract_rows_from_file(file_path):
    """Extract rows (sentences) from a file and normalize them."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            rows = [normalize_text(line) for line in f if line.strip()]
        return rows
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def capture_window(window_title):
    """Capture a specific window by title and return it as a PIL image."""
    try:
        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
            print(f"No window found with title: {window_title}")
            return None
        window = windows[0]  # Assuming the first match is the correct one

        # Get the bounding box of the window
        bbox = (window.left, window.top, window.right, window.bottom)

        # Capture the window region using mss
        with mss.mss() as sct:
            screenshot = sct.grab(bbox)
            # Convert screenshot to PIL Image
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            return img
    except Exception as e:
        print(f"Error capturing window: {e}")
        return None

def extract_text_from_window(window_title):
    """Extract and normalize text from a specific window using OCR."""
    window_image = capture_window(window_title)
    if window_image:
        try:
            extracted_text = pytesseract.image_to_string(window_image)
            print("Extracted OCR Text:", extracted_text)
            return normalize_text(extracted_text)
        except Exception as e:
            print(f"Error extracting text from window: {e}")
            return ""
    else:
        return ""

def compare_rows_in_window(file_path, window_title):
    """Compare rows in the file with normalized text extracted from a specific window."""
    window_text = extract_text_from_window(window_title)
    file_rows = extract_rows_from_file(file_path)

    # Rows must fully match within the window text
    missing_rows = [row for row in file_rows if row not in window_text]
    present_rows = [row for row in file_rows if row in window_text]

    return {
        "present_rows": present_rows,
        "missing_rows": missing_rows
    }

if __name__ == "__main__":
    file_path = "dataset.tsv"  # Replace with your uploaded file path
    window_title = "Chrome"  # Replace with the specific window title

    while True:
        print("\nAnalyzing target window...")
        results = compare_rows_in_window(file_path, window_title)
        print("\nRows Present in Target Window:")
        for row in results["present_rows"]:
            print(f"- {row}")

        # print("\nRows Missing in Target Window:")
        # for row in results["missing_rows"]:
        #     print(f"- {row}")

        # Pause before the next capture (adjust as needed)
        time.sleep(5)
