import os
import io
import fitz  
import pdfplumber 
from PIL import Image

def extract_pdf_contents(
    filepath: str,
    output_dir: str = "extracted_data",
    ):
   
    base = os.path.splitext(os.path.basename(filepath))[0]
    root = os.path.join(output_dir, base)
    tbl_dir = os.path.join(root, "tables")
    img_dir = os.path.join(root, "images")
    os.makedirs(tbl_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    #  pdfplumber extracts text and tables
    full_text = []
    table_paths = []
    with pdfplumber.open(filepath) as pdf:
        for pageno, page in enumerate(pdf.pages, start=1):
            # -- Text
            text = page.extract_text() or ""
            full_text.append(text)

            #  Advanced table detection
            tables = page.find_tables()
            for idx, table in enumerate(tables, start=1):
                # table.extract() returns list of rows
                rows = table.extract()
                csv_path = os.path.join(tbl_dir, f"table_p{pageno}_{idx}.csv")
                with open(csv_path, "w", encoding="utf8") as f:
                    for row in rows:
                        clean = [cell.replace(",", " ") if cell else "" for cell in row]
                        f.write(",".join(clean) + "\n")
                table_paths.append(csv_path)

    # pymupdf extract iamges only
    image_paths = []
    doc = fitz.open(filepath)
    for pageno, page in enumerate(doc, start=1):
        for img_index, img_info in enumerate(page.get_images(full=True), start=1):
            xref = img_info[0]
            img_dict = doc.extract_image(xref)
            img_bytes = img_dict["image"]
            ext = img_dict.get("ext", "png")
            pil_img = Image.open(io.BytesIO(img_bytes))
            out_path = os.path.join(img_dir, f"p{pageno}_{img_index}.{ext}")
            pil_img.save(out_path)
            image_paths.append(out_path)

    return {
        "text": "\n\n".join(full_text).strip(),
        "tables": table_paths,
        "images": image_paths,
    }
