import fitz  # PyMuPDF - library to read and work with PDFs
import re
import json
from pathlib import Path
from statistics import mean

# =========================
# Configuration
# =========================
# Common section names that usually appear in research papers.
# We use these to help guess if a block is a section heading.
KNOWN_HEADINGS = {
    "abstract", "introduction", "related work", "background", "preliminaries",
    "method", "methodology", "approach", "experiment", "evaluation",
    "results", "analysis", "discussion", "conclusion", "future work", "references"
}

# Patterns to catch numbered headings like:
# "1. Introduction", "1.1 Background", or "I. Related Work"
NUMBERING_REGEXES = [
    r'^\s*\d+(\.\d+)*\s+[A-Z]',  # Matches decimal numbering
    r'^\s*[IVXLC]+\.\s+[A-Z]',   # Matches Roman numeral numbering
]

# =========================
# Step 1: Read PDF and extract text with layout info
# =========================
def extract_blocks_with_layout(pdf_path):
    """
    Reads a PDF and pulls out chunks of text (blocks) along with
    font size, position, and page number — so we can later guess
    which ones are section titles.
    """
    doc = fitz.open(pdf_path)
    all_blocks = []
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                text = "".join([span["text"] for span in line["spans"]]).strip()
                if not text:
                    continue
                # Safely convert font sizes to float
                font_sizes = []
                for span in line["spans"]:
                    try:
                        font_sizes.append(float(span["size"]))
                    except (ValueError, TypeError):
                        font_sizes.append(12.0)  # default font size
                
                avg_font = mean(font_sizes) if font_sizes else 12.0
                
                # Safely convert y0 to float
                try:
                    y0 = float(block["bbox"][1])
                except (ValueError, TypeError):
                    y0 = 0.0
                
                all_blocks.append({
                    "text": text,
                    "font_size": avg_font,
                    "y0": y0,  # Top Y-coordinate of the block
                    "page": page_num
                })
    return all_blocks

# =========================
# Step 2: Helpers to check if a block looks like a heading
# =========================
def is_all_caps(text):
    return text.isupper() and len(text) > 3

def is_title_case(text):
    return text.istitle()

def matches_numbering(text):
    return any(re.match(rgx, text) for rgx in NUMBERING_REGEXES)

# =========================
# Step 3: Score blocks to guess headings
# =========================
def compute_scores(blocks):
    """
    Gives each text block a 'heading-likelihood' score
    based on font size, capitalization, numbering, and spacing.
    """
    # Safely extract font sizes and ensure they are floats
    font_sizes = []
    for b in blocks:
        try:
            font_sizes.append(float(b["font_size"]))
        except (ValueError, TypeError):
            font_sizes.append(12.0)
    
    avg_font = mean(font_sizes) if font_sizes else 12.0

    for i, block in enumerate(blocks):
        score = 0

        # Safely convert font_size to float before comparison
        try:
            font_size = float(block["font_size"])
            # Bigger font than average → more likely a heading
            if font_size >= avg_font * 1.15:
                score += 3
        except (ValueError, TypeError):
            # If font_size conversion fails, skip this scoring
            pass

        # ALL CAPS or Title Case gives extra points
        if is_all_caps(block["text"]):
            score += 1
        if is_title_case(block["text"]):
            score += 1

        # Matches something like "1. Introduction" or "II. Background"
        if matches_numbering(block["text"]):
            score += 2

        # Extra vertical gap before this block → might be a heading
        if i > 0:
            try:
                y_gap = float(block["y0"]) - float(blocks[i - 1]["y0"])
                if y_gap > 20:  # tweak as needed per document style
                    score += 1
            except (ValueError, TypeError):
                # If y0 conversion fails, skip gap scoring
                pass

        block["score"] = score
    return blocks

# =========================
# Step 4: Turn scored blocks into structured sections
# =========================
def process_pdf_to_sections(pdf_path, output_dir=None, threshold=4):
    """
    Goes through the PDF, figures out where headings are,
    and groups the text under each heading into a clean JSON structure.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the chunks JSON (optional)
        threshold: Score threshold for identifying headings
    
    Returns:
        tuple: (sections, chunks_path) if output_dir provided, else just sections
    """
    # Handle the case where output_dir is passed as second parameter
    if isinstance(output_dir, (int, float)):
        # output_dir is actually threshold, no output_dir provided
        threshold = int(output_dir)
        output_dir = None
    elif isinstance(output_dir, str) and threshold == 4:
        # output_dir is provided as string, keep default threshold
        pass
    blocks = extract_blocks_with_layout(pdf_path)
    scored_blocks = compute_scores(blocks)

    sections = []
    current_section = None

    for block in scored_blocks:
        text = block["text"]
        # Safely convert score to int
        try:
            score = int(block["score"])
        except (ValueError, TypeError):
            score = 0

        if score >= threshold:
            # Found a new heading → save previous section if it exists
            if current_section and current_section["text"].strip():
                sections.append(current_section)

            # Make the heading look nice (title case if it’s known)
            title = text.strip()
            title_lower = title.lower()
            if any(known in title_lower for known in KNOWN_HEADINGS):
                section_title = title.title()
            else:
                section_title = title

            # Start a fresh section
            current_section = {"section": section_title, "text": ""}

        else:
            # Not a heading → add this text to the current section
            if current_section:
                current_section["text"] += text + "\n"
            else:
                # If no section started yet, put it under "Unknown"
                current_section = {"section": "Unknown", "text": text + "\n"}

    # Add the very last section to the list
    if current_section and current_section["text"].strip():
        sections.append(current_section)

    # If output_dir is provided, save to file and return path
    if output_dir:
        from pathlib import Path
        import os
        
        pdf_name = Path(pdf_path).stem
        chunks_filename = f"{pdf_name}.chunks.json"
        chunks_path = os.path.join(output_dir, chunks_filename)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Save sections to JSON file
        save_sections_as_json(sections, chunks_path)
        
        return sections, chunks_path
    
    return sections

# =========================
# Step 5: Save the structured sections as JSON
# =========================
def save_sections_as_json(sections, output_path):
    """
    Saves the list of sections to a JSON file so other tools can read it.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sections, f, indent=2, ensure_ascii=False)


# # =========================
# # Step 6: Run from the command line
# # =========================
# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) < 2:
#         print("Usage: python pdf_chunker.py path/to/document.pdf")
#         sys.exit(1)

#     pdf_path = sys.argv[1]
#     output_path = Path(pdf_path).with_suffix(".chunks.json")

#     sections = process_pdf_to_sections(pdf_path)
#     save_sections_as_json(sections, output_path)

#     print(f" Done! Sections saved to {output_path}")
