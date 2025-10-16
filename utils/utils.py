# This contains the utility functions used across the application.
# importing the necessary libraries
import os
import re
import fitz

# importing the necessary components
import Config


def create_required_directories():
    """Creates the required directories if they do not exist."""
    if not os.path.exists(Config.DATA_DIRECTORY):
        os.makedirs(Config.DATA_DIRECTORY)
    if not os.path.exists(Config.RESUME_DIRECTORY):
        os.makedirs(Config.RESUME_DIRECTORY)
    if not os.path.exists(Config.JOB_DESCRIPTION_DIRECTORY):
        os.makedirs(Config.JOB_DESCRIPTION_DIRECTORY)
    if not os.path.exists(Config.RESUME_SUMMARY):
        os.makedirs(Config.RESUME_SUMMARY)


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Robust PDF text extraction using PyMuPDF.
    Keeps reading order page-by-page and joins with \n\n.
    """
    doc = fitz.open(pdf_path)
    pages = []
    for i in range(len(doc)):
        pages.append(doc[i].get_text("text"))
    text = "\n\n".join(pages)
    # normalize whitespace lightly
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text
