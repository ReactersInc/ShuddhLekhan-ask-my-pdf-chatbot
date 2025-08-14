import fitz 

def extract_text_from_pdf(filepath):
    try:
        doc = fitz.open(filepath)
        all_blocks = []

        for page in doc:
            blocks = page.get_text("blocks")  # Each block: (x0, y0, x1, y1, "text", block_no, ...)
            for block in blocks:
                x0, y0, x1, y1, text, *_ = block
                if text.strip():  # Ignore empty blocks
                    all_blocks.append((y0, x0, text.strip()))

        # Sort blocks by vertical and then horizontal position
        all_blocks.sort(key=lambda b: (b[0], b[1]))

        # Join all text blocks with a double newline (paragraph separator)
        combined_text = "\n\n".join([b[2] for b in all_blocks])
        return combined_text.strip()

    except Exception as e:
        print(f"Error extracting context-preserving text: {e}")
        return ""
