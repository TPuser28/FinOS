import os, json, zipfile, tarfile, csv, psycopg2, base64, hashlib
from io import BytesIO
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import ast
import re
import json
from openai import OpenAI
from PIL import Image
from mistralai.client import MistralClient
from pgvector.psycopg2 import register_vector

# Dossiers de travail
UPLOAD_DIR = "Uploads"
MARKDOWN_DIR = "Markdown"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MARKDOWN_DIR, exist_ok=True)

# Extensions texte supportées
SUPPORTED_EXTENSIONS = {
    ".md", ".yaml", ".yml", ".json", ".xml", ".csv",
    ".log", ".txt", ".diff", ".patch", ".info", ".env", ".sh",
    ".tf", ".dockerfile"
}

# Connexions externes
PG_CONFIG = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": int(os.getenv("PG_PORT", "5532")),
    "database": os.getenv("PG_DATABASE", "ai"),
    "user": os.getenv("PG_USER", "ai"),
    "password": os.getenv("PG_PASSWORD", "ai")
}
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Validate required API keys
if not OPENAI_API_KEY:
    print("⚠️  Warning: OPENAI_API_KEY not set. OpenAI embeddings will not work.")
if not MISTRAL_API_KEY:
    print("⚠️  Warning: MISTRAL_API_KEY not set. Mistral OCR will not work.")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
mistral_client = MistralClient(api_key=MISTRAL_API_KEY) if MISTRAL_API_KEY else None

# DB pg / pgvector
def get_pg_connection():
    conn = psycopg2.connect(**PG_CONFIG)
    register_vector(conn)
    return conn

def init_pgvector():
    conn = get_pg_connection(); cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            filename TEXT,
            content TEXT,
            embedding vector(1536),
            content_hash TEXT UNIQUE
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS document_chunks (
            id SERIAL PRIMARY KEY,
            document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            embedding vector(1536)
        );
    """)
    conn.commit(); cur.close(); conn.close()

# Embeddings + utilitaires
def embed_text(text: str) -> List[float]:
    if not client:
        raise RuntimeError("OpenAI client not configured. Set OPENAI_API_KEY environment variable.")
    resp = client.embeddings.create(model="text-embedding-3-small", input=text)
    return resp.data[0].embedding

def compute_content_hash(content_str: str) -> str:
    return hashlib.sha256(content_str.encode("utf-8")).hexdigest()

def chunk_text(text: str, max_chars: int = 7200, overlap: int = 800) -> list[str]:
    if len(text) <= max_chars: return [text]
    chunks, start = [], 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        chunks.append(text[start:end])
        if end == len(text): break
        start = max(0, end - overlap)
    return chunks

# Lecture / extraction / OCR / images
def read_supported_files_from(folder: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    if not os.path.exists(folder): return out
    for root, _, files in os.walk(folder):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            is_dockerfile = file.lower() == "dockerfile"
            if (ext not in SUPPORTED_EXTENSIONS) and (not is_dockerfile):
                continue
            path = os.path.join(root, file)
            try:
                if ext == ".csv":
                    with open(path, "r", encoding="utf-8") as f:
                        out[file] = list(csv.reader(f))
                else:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if ext == ".json":
                            try: content = json.loads(content)
                            except json.JSONDecodeError: pass
                        out[file] = content
            except Exception as e:
                out[file] = f"Erreur lecture : {e}"
    return out

def extract_archive(file_path: str, extract_dir: str) -> str:
    os.makedirs(extract_dir, exist_ok=True)
    if file_path.endswith((".zip", ".jar", ".war", ".ear")):
        with zipfile.ZipFile(file_path, 'r') as z: z.extractall(extract_dir)
    elif file_path.endswith((".tar.gz", ".tgz", ".tar")):
        with tarfile.open(file_path, 'r:*') as t: t.extractall(extract_dir)
    return extract_dir

def extract_nested_tars(root_dir: str):
    for r, _, files in os.walk(root_dir):
        for f in files:
            if not f.endswith(".tar"): continue
            p = os.path.join(r, f)
            try:
                sub = os.path.join(r, f"{os.path.splitext(f)[0]}_extracted")
                os.makedirs(sub, exist_ok=True)
                extract_archive(p, sub)
            except Exception:
                continue

def analyze_image_to_text_blob(file_path: str) -> Dict[str, Any]:
    try:
        with Image.open(file_path) as img:
            meta = {"filename": os.path.basename(file_path),
                    "format": img.format, "size": img.size, "mode": img.mode}
            buf = BytesIO(); img.save(buf, format="PNG")
            meta["base64_png"] = base64.b64encode(buf.getvalue()).decode("utf-8")
            return meta
    except Exception as e:
        return {"error": str(e), "filename": os.path.basename(file_path)}

def ocr_pdf_to_markdown(pdf_path: str) -> str:
    if not mistral_client:
        raise RuntimeError("Mistral client not configured. Set MISTRAL_API_KEY environment variable.")
    uploaded = mistral_client.files.upload(
        file={"file_name": os.path.basename(pdf_path), "content": open(pdf_path, "rb")},
        purpose="ocr"
    )
    signed = mistral_client.files.get_signed_url(file_id=uploaded.id)
    ocr = mistral_client.ocr.process(
        model="mistral-ocr-latest",
        document={"type": "document_url", "document_url": signed.url},
        include_image_base64=False,
    )
    md = "\n".join([p.markdown for p in ocr.pages])
    out_path = os.path.join(MARKDOWN_DIR, f"{os.path.splitext(os.path.basename(pdf_path))[0]}.md")
    with open(out_path, "w", encoding="utf-8") as f: f.write(md)
    return md

def ingest_pdf_with_ocr(pdf_path: str) -> dict:
    md = ocr_pdf_to_markdown(pdf_path)
    virtual_name = f"{os.path.splitext(os.path.basename(pdf_path))[0]}.md"
    payload = {virtual_name: md}
    store_in_pgvector(payload)
    return payload

# Indexation (documents + chunks)
def store_in_pgvector(files_dict: Dict[str, Any]):
    if not files_dict: return
    conn = get_pg_connection(); cur = conn.cursor()
    for filename, content in files_dict.items():
        content_str = json.dumps(content, ensure_ascii=False) if isinstance(content, (dict, list)) else str(content)
        content_hash = compute_content_hash(content_str)
        cur.execute("SELECT id FROM documents WHERE content_hash=%s;", (content_hash,))
        if cur.fetchone():
            print(f"⚠️  {filename} déjà en base, ignoré."); continue

        doc_vec = embed_text(content_str)
        cur.execute(
            "INSERT INTO documents (filename, content, embedding, content_hash) VALUES (%s, %s, %s, %s) RETURNING id;",
            (filename, content_str, doc_vec, content_hash)
        )
        doc_id = cur.fetchone()[0]

        chunks = chunk_text(content_str)
        for idx, ch in enumerate(chunks):
            ch_vec = embed_text(ch)
            cur.execute(
                "INSERT INTO document_chunks (document_id, chunk_index, content, embedding) VALUES (%s, %s, %s, %s);",
                (doc_id, idx, ch, ch_vec)
            )

        print(f"✅ {filename} ajouté (doc_id={doc_id}, chunks={len(chunks)}).")
    conn.commit(); cur.close(); conn.close()

# Recherche + KB
def search_pgvector_chunks(query: str, top_k: int = 8):
    qv = embed_text(query)
    conn = get_pg_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT d.filename, dc.content, 1 - (dc.embedding <=> %s) AS sim
        FROM document_chunks dc
        JOIN documents d ON d.id = dc.document_id
        ORDER BY sim DESC
        LIMIT %s;
    """, (qv, top_k))
    rows = cur.fetchall(); cur.close(); conn.close()
    return [{"filename": r[0], "content": r[1], "similarity": float(r[2])} for r in rows]

class KnowledgeBase:
    def __init__(self, top_k: int = 8):
        self.top_k = top_k
    def search(self, query: str):
        return search_pgvector_chunks(query, self.top_k)
    def context_text(self, query: str) -> str:
        res = self.search(query)
        return "\n\n".join([f"### {r['filename']} (sim={r['similarity']:.2f})\n{r['content'][:1800]}" for r in res])
