import os, shutil, redis, psycopg2,uvicorn
from psycopg2.extras import RealDictCursor
from typing import Optional
from datetime import datetime, timezone
from rq import Queue
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from pydantic import BaseModel
from contextlib import asynccontextmanager
from managers_registry import MANAGER_BY_MODULE
from fastapi.middleware.cors import CORSMiddleware
from tools import UPLOAD_DIR, init_pgvector, KnowledgeBase
from ingestion_queue.tasks import (
    ingest_archive_job, ingest_pdf_job, ingest_image_job, ingest_single_file_job
)

# ---------- Config DB (même instance que pgvector) ----------

PG_CONFIG = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": int(os.getenv("PG_PORT", "5532")),
    "database": os.getenv("PG_DATABASE", "ai"),
    "user": os.getenv("PG_USER", "ai"),
    "password": os.getenv("PG_PASSWORD", "ai")
}

def db_conn():
    return psycopg2.connect(cursor_factory=RealDictCursor, **PG_CONFIG)

# ---------- Modules OS 10 (pour la colonne gauche de l'UI) ----------
MODULES = [
    {"key": "code-quality",       "name": "Code Quality Module"},
    {"key": "project-management", "name": "Project Management Module"},
    {"key": "devops",             "name": "DevOps Module"},
    {"key": "documentation",      "name": "Documentation Module"},
    {"key": "testing",            "name": "Testing Module"},
    {"key": "security",           "name": "Security Module"},
]
MODULE_KEYS = {m["key"] for m in MODULES}

# ---------- DDL minimal (tables chats + messages) ----------
def init_chat_tables():
    conn = db_conn(); cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id SERIAL PRIMARY KEY,
            module_key TEXT NOT NULL,
            title TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            chat_id INTEGER REFERENCES chats(id) ON DELETE CASCADE,
            role TEXT NOT NULL,         -- 'user' | 'assistant'
            content TEXT NOT NULL,
            agent_key TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    conn.commit(); cur.close(); conn.close()

# ---------- Lifespan (startup/shutdown) ----------
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dossiers
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # Tables vecteur (documents, chunks) + tables de chat
    init_pgvector()
    init_chat_tables()
    # Redis / RQ attachés au state de l'app
    app.state.redis_conn = redis.from_url(REDIS_URL)
    app.state.q = Queue("ingestion", connection=app.state.redis_conn)
    yield
    # (shutdown) rien à fermer ici

# ---------- Création de l'app AVEC lifespan ----------
app = FastAPI(lifespan=lifespan)

# ---------- Middleware CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Hook routeur d'agent (sans branchement de managers pour l'instant) ----------
class AgentRouter:
    """
    Tu enregistreras plus tard tes Team Managers avec:
      AgentRouter.register("code-quality", ton_handler)
    Ici, aucun handler n'est branché -> fallback KB-only.
    """
    _handlers = {}

    @classmethod
    def register(cls, module_key: str, handler):
        cls._handlers[module_key] = handler

    @classmethod
    def handle(cls, module_key: str, chat_id: int, user_text: str, kb: KnowledgeBase) -> str:
        h = cls._handlers.get(module_key)
        if h:
            return h(module_key, chat_id, user_text, kb)
        # Fallback: réponse basée uniquement sur la KB
        context = kb.context_text(user_text)
        if not context:
            return ("Je n'ai pas assez de contexte indexé pour répondre. "
                    "Uploade des fichiers pertinents dans ce module, puis réessaie.")
        return f"Contexte pertinent trouvé :\n\n{context}\n\n(Réponse générée en mode KB-only.)"


def _make_handler(team):
    # Appelle le manager agno et renvoie sa réponse textuelle
    def _h(module_key: str, chat_id: int, user_text: str, kb):
        try:
            resp = team.run(user_text)
        except AttributeError:
            resp = team.chat(user_text)
        return getattr(resp, "content", None) or str(resp)
    return _h

# Enregistrement: clé de module -> handler
for _module_key, _team in MANAGER_BY_MODULE.items():
    AgentRouter.register(_module_key, _make_handler(_team))


# ---------- Schémas Pydantic ----------
class NewChat(BaseModel):
    title: Optional[str] = None

class NewMessage(BaseModel):
    text: str
    agent_key: Optional[str] = None  # réservé pour plus tard

class UploadMeta(BaseModel):
    pass  # placeholder si tu ajoutes tenant/tags/module ensuite

# ---------- Endpoints Modules (colonne gauche) ----------
@app.get("/modules")
def list_modules():
    return MODULES

# ---------- Endpoints Chats (liste + création par module) ----------
@app.get("/modules/{module_key}/chats")
def list_chats(module_key: str, limit: int = 50, offset: int = 0):
    if module_key not in MODULE_KEYS:
        raise HTTPException(status_code=404, detail="Module inconnu")
    conn = db_conn(); cur = conn.cursor()
    cur.execute("""
        SELECT id, module_key, title, created_at
        FROM chats
        WHERE module_key = %s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s;
    """, (module_key, limit, offset))
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows

@app.post("/modules/{module_key}/chats")
def create_chat(module_key: str, body: NewChat):
    if module_key not in MODULE_KEYS:
        raise HTTPException(status_code=404, detail="Module inconnu")
    title = body.title or f"Chat {datetime.now(timezone.utc).isoformat(timespec='seconds')}"
    conn = db_conn(); cur = conn.cursor()
    cur.execute(
        "INSERT INTO chats (module_key, title) VALUES (%s, %s) RETURNING id, module_key, title, created_at;",
        (module_key, title)
    )
    row = cur.fetchone(); conn.commit(); cur.close(); conn.close()
    return row

# ---------- Endpoints Messages (historique + envoi) ----------
@app.get("/chats/{chat_id}/messages")
def get_messages(chat_id: int, limit: int = 100, offset: int = 0):
    conn = db_conn(); cur = conn.cursor()
    cur.execute("SELECT id, module_key, title FROM chats WHERE id=%s;", (chat_id,))
    chat = cur.fetchone()
    if not chat:
        cur.close(); conn.close()
        raise HTTPException(status_code=404, detail="Chat introuvable")

    cur.execute("""
        SELECT id, role, content, agent_key, created_at
        FROM messages
        WHERE chat_id=%s
        ORDER BY created_at ASC
        LIMIT %s OFFSET %s;
    """, (chat_id, limit, offset))
    msgs = cur.fetchall(); cur.close(); conn.close()
    return {"chat": chat, "messages": msgs}

@app.post("/chats/{chat_id}/messages")
def post_message(chat_id: int, body: NewMessage):
    user_text = (body.text or "").strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Message vide")

    conn = db_conn(); cur = conn.cursor()
    cur.execute("SELECT id, module_key FROM chats WHERE id=%s;", (chat_id,))
    chat = cur.fetchone()
    if not chat:
        cur.close(); conn.close()
        raise HTTPException(status_code=404, detail="Chat introuvable")

    module_key = chat["module_key"]

    # Enregistrer le message utilisateur
    cur.execute(
        "INSERT INTO messages (chat_id, role, content, agent_key) VALUES (%s, %s, %s, %s) RETURNING id, created_at;",
        (chat_id, "user", user_text, None)
    )
    user_msg = cur.fetchone()

    # Appeler le routeur (aucun manager branché => fallback KB-only)
    kb = KnowledgeBase(top_k=8)
    assistant_text = AgentRouter.handle(module_key, chat_id, user_text, kb)

    # Enregistrer la réponse assistant
    cur.execute(
        "INSERT INTO messages (chat_id, role, content, agent_key) VALUES (%s, %s, %s, %s) RETURNING id, created_at;",
        (chat_id, "assistant", assistant_text, body.agent_key)
    )
    asst_msg = cur.fetchone()

    conn.commit(); cur.close(); conn.close()
    return {
        "user_message": {"id": user_msg["id"], "created_at": user_msg["created_at"], "content": user_text},
        "assistant_message": {"id": asst_msg["id"], "created_at": asst_msg["created_at"], "content": assistant_text},
    }

# ---------- Upload + Jobs d’ingestion (asynchrone via RQ) ----------
@app.post("/upload")
async def upload(request: Request, file: UploadFile = File(...), meta: UploadMeta = UploadMeta()):
    """
    Sauvegarde le fichier dans Uploads/ puis enfile un job d'ingestion selon l'extension.
    L'UI du module courant peut appeler cet endpoint.
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    fname = file.filename.lower()
    q: Queue = request.app.state.q
    if fname.endswith((".zip", ".jar", ".war", ".ear", ".tar.gz", ".tgz", ".tar")):
        job = q.enqueue(ingest_archive_job, file_path)
    elif fname.endswith(".pdf"):
        job = q.enqueue(ingest_pdf_job, file_path)
    elif fname.endswith((".png", ".jpg", ".jpeg")):
        job = q.enqueue(ingest_image_job, file_path)
    else:
        job = q.enqueue(ingest_single_file_job, file_path)

    return {"message": f"{file.filename} reçu, ingestion en cours", "job_id": job.get_id()}

@app.get("/jobs/{job_id}")
def job_status(job_id: str, request: Request):
    """Permet au frontend de suivre l'état d'un job d'ingestion."""
    from rq.job import Job
    redis_conn = request.app.state.redis_conn
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception:
        raise HTTPException(status_code=404, detail="Job introuvable")
    return {
        "job_id": job_id,
        "status": job.get_status(),
        "result": job.result if job.is_finished else None,
    }

@app.get("/health")
def health_check():
    """Health check endpoint for Docker health checks"""
    try:
        # Test database connection
        conn = db_conn()
        conn.close()

        # Test Redis connection
        redis_conn = redis.from_url(REDIS_URL)
        redis_conn.ping()

        return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)