import os
from typing import Dict, Any
from tools import (
    read_supported_files_from, extract_archive, extract_nested_tars,
    analyze_image_to_text_blob, ingest_pdf_with_ocr, store_in_pgvector
)

def ingest_archive_job(archive_path: str, extract_root: str = "Uploads/extracted") -> Dict[str, Any]:
    base = os.path.splitext(os.path.basename(archive_path))[0]
    extract_dir = os.path.join(extract_root, base)
    extract_archive(archive_path, extract_dir)
    extract_nested_tars(extract_dir)
    files_content = read_supported_files_from(extract_dir)
    store_in_pgvector(files_content)
    return {"indexed": list(files_content.keys())}

def ingest_pdf_job(pdf_path: str) -> Dict[str, Any]:
    files_content = ingest_pdf_with_ocr(pdf_path)  # store_in_pgvector déjà appelé
    return {"indexed": list(files_content.keys())}

def ingest_image_job(image_path: str) -> Dict[str, Any]:
    blob = analyze_image_to_text_blob(image_path)
    files_content = {os.path.basename(image_path): blob}
    store_in_pgvector(files_content)
    return {"indexed": list(files_content.keys())}

def ingest_single_file_job(file_path: str) -> Dict[str, Any]:
    folder = os.path.dirname(file_path); name = os.path.basename(file_path)
    all_map = read_supported_files_from(folder)
    content = all_map.get(name)
    files_content = {name: content} if content is not None else {}
    store_in_pgvector(files_content)
    return {"indexed": list(files_content.keys())}
