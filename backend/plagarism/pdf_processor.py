"""
Purpose:
--------
Provides functions to process PDFs into logical sections and save
those sections in a structured JSON format. Acts as a thin wrapper
over the `section_chunker` utility.

Responsibilities:
-----------------
- Call `process_pdf_to_sections()` to extract sections from a PDF.
- Save processed sections to a `.chunks.json` file.
- Return both the section data and the output file path.

Note:
-----
This service only handles PDF-to-section transformation and saving
the results. No keyword extraction or plagiarism checking is done here.
"""

import os
from pathlib import Path
from plagarism.section_chunker import process_pdf_to_sections, save_sections_as_json

def process_pdf(file_path, result_dir):
    sections = process_pdf_to_sections(file_path)
    chunks_json_path = os.path.join(result_dir, Path(file_path).stem + ".chunks.json")
    save_sections_as_json(sections, chunks_json_path)
    return sections, chunks_json_path
