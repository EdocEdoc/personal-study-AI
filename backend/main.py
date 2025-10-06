from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import PyPDF2
import docx
import io
import hashlib
import sqlite3
from datetime import datetime, timedelta
import secrets

app = FastAPI(
    title="AI Study Tool API",
    description="API for parsing and managing study documents",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Database initialization
def init_db():
    conn = sqlite3.connect('study_tool.db')
    cursor = conn.cursor()
    
    # Documents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_hash TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            content TEXT NOT NULL,
            file_size INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # App credentials table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_username TEXT UNIQUE NOT NULL,
            access_token TEXT UNIQUE NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Bearer tokens table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bearer_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE NOT NULL,
            app_username TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (app_username) REFERENCES app_credentials(app_username)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# Pydantic models
class AuthRequest(BaseModel):
    app_username: str
    access_token: str

class AuthResponse(BaseModel):
    bearer_token: str
    expires_in: int
    token_type: str = "Bearer"

class AppCredentialCreate(BaseModel):
    app_username: str
    access_token: str

class AppCredentialResponse(BaseModel):
    id: int
    app_username: str
    is_active: bool
    created_at: str

class DocumentResponse(BaseModel):
    id: int
    file_hash: str
    filename: str
    content: str
    file_size: int
    created_at: str
    was_cached: bool = False

class DocumentUpdate(BaseModel):
    filename: Optional[str] = None
    content: Optional[str] = None

# Database helpers
def get_db():
    conn = sqlite3.connect('study_tool.db')
    conn.row_factory = sqlite3.Row
    return conn

def calculate_file_hash(content: bytes) -> str:
    """Calculate SHA256 hash of file content"""
    return hashlib.sha256(content).hexdigest()

def parse_pdf(file_content: bytes) -> str:
    """Parse PDF file and extract text"""
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing PDF: {str(e)}")

def parse_docx(file_content: bytes) -> str:
    """Parse DOCX file and extract text"""
    try:
        doc_file = io.BytesIO(file_content)
        doc = docx.Document(doc_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing DOCX: {str(e)}")

def parse_txt(file_content: bytes) -> str:
    """Parse TXT file"""
    try:
        return file_content.decode('utf-8').strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing TXT: {str(e)}")

def parse_file(filename: str, content: bytes) -> str:
    """Parse file based on extension"""
    extension = filename.lower().split('.')[-1]
    
    if extension == 'pdf':
        return parse_pdf(content)
    elif extension in ['docx', 'doc']:
        return parse_docx(content)
    elif extension == 'txt':
        return parse_txt(content)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF, DOCX, and TXT are supported.")

# Authentication
async def verify_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify bearer token"""
    token = credentials.credentials
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT bt.app_username, bt.expires_at, ac.is_active
        FROM bearer_tokens bt
        JOIN app_credentials ac ON bt.app_username = ac.app_username
        WHERE bt.token = ? AND bt.expires_at > datetime('now')
    ''', (token,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result or not result['is_active']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return result['app_username']

# Auth endpoints
@app.post("/auth/token", response_model=AuthResponse, tags=["Authentication"])
async def get_bearer_token(auth: AuthRequest):
    """
    Authenticate and get bearer token
    
    Provide app_username and access_token to receive a bearer token
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Verify credentials
    cursor.execute('''
        SELECT app_username, is_active 
        FROM app_credentials 
        WHERE app_username = ? AND access_token = ?
    ''', (auth.app_username, auth.access_token))
    
    result = cursor.fetchone()
    
    if not result or not result['is_active']:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Generate bearer token
    bearer_token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=24)
    
    cursor.execute('''
        INSERT INTO bearer_tokens (token, app_username, expires_at)
        VALUES (?, ?, ?)
    ''', (bearer_token, auth.app_username, expires_at))
    
    conn.commit()
    conn.close()
    
    return AuthResponse(
        bearer_token=bearer_token,
        expires_in=86400  # 24 hours in seconds
    )

# File upload endpoint
@app.post("/documents/upload", response_model=DocumentResponse, tags=["Documents"])
async def upload_file(
    file: UploadFile = File(...),
    username: str = Depends(verify_bearer_token)
):
    """
    Upload and parse a document (PDF, DOCX, or TXT)
    
    Returns cached result if file was previously uploaded
    """
    # Read file content
    content = await file.read()
    file_hash = calculate_file_hash(content)
    file_size = len(content)
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if file already exists
    cursor.execute('SELECT * FROM documents WHERE file_hash = ?', (file_hash,))
    existing = cursor.fetchone()
    
    if existing:
        conn.close()
        return DocumentResponse(
            id=existing['id'],
            file_hash=existing['file_hash'],
            filename=existing['filename'],
            content=existing['content'],
            file_size=existing['file_size'],
            created_at=existing['created_at'],
            was_cached=True
        )
    
    # Parse new file
    parsed_text = parse_file(file.filename, content)
    
    # Save to database
    cursor.execute('''
        INSERT INTO documents (file_hash, filename, content, file_size)
        VALUES (?, ?, ?, ?)
    ''', (file_hash, file.filename, parsed_text, file_size))
    
    doc_id = cursor.lastrowid
    conn.commit()
    
    # Fetch created document
    cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
    document = cursor.fetchone()
    conn.close()
    
    return DocumentResponse(
        id=document['id'],
        file_hash=document['file_hash'],
        filename=document['filename'],
        content=document['content'],
        file_size=document['file_size'],
        created_at=document['created_at'],
        was_cached=False
    )

# Document CRUD
@app.get("/documents", response_model=List[DocumentResponse], tags=["Documents"])
async def list_documents(
    skip: int = 0,
    limit: int = 10,
    username: str = Depends(verify_bearer_token)
):
    """List all documents with pagination"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM documents 
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
    ''', (limit, skip))
    
    documents = cursor.fetchall()
    conn.close()
    
    return [DocumentResponse(**dict(doc), was_cached=False) for doc in documents]

@app.get("/documents/{document_id}", response_model=DocumentResponse, tags=["Documents"])
async def get_document(
    document_id: int,
    username: str = Depends(verify_bearer_token)
):
    """Get a specific document by ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM documents WHERE id = ?', (document_id,))
    document = cursor.fetchone()
    conn.close()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(**dict(document), was_cached=False)

@app.put("/documents/{document_id}", response_model=DocumentResponse, tags=["Documents"])
async def update_document(
    document_id: int,
    update: DocumentUpdate,
    username: str = Depends(verify_bearer_token)
):
    """Update a document's filename or content"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if document exists
    cursor.execute('SELECT * FROM documents WHERE id = ?', (document_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Build update query
    updates = []
    params = []
    
    if update.filename is not None:
        updates.append("filename = ?")
        params.append(update.filename)
    
    if update.content is not None:
        updates.append("content = ?")
        params.append(update.content)
    
    if not updates:
        conn.close()
        raise HTTPException(status_code=400, detail="No updates provided")
    
    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(document_id)
    
    query = f"UPDATE documents SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, params)
    conn.commit()
    
    # Fetch updated document
    cursor.execute('SELECT * FROM documents WHERE id = ?', (document_id,))
    document = cursor.fetchone()
    conn.close()
    
    return DocumentResponse(**dict(document), was_cached=False)

@app.delete("/documents/{document_id}", tags=["Documents"])
async def delete_document(
    document_id: int,
    username: str = Depends(verify_bearer_token)
):
    """Delete a document"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM documents WHERE id = ?', (document_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Document not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Document deleted successfully"}

# App Credentials CRUD
@app.post("/admin/credentials", response_model=AppCredentialResponse, tags=["Admin"])
async def create_app_credential(cred: AppCredentialCreate):
    """Create new app credentials (admin endpoint - should be protected in production)"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO app_credentials (app_username, access_token)
            VALUES (?, ?)
        ''', (cred.app_username, cred.access_token))
        
        cred_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute('SELECT * FROM app_credentials WHERE id = ?', (cred_id,))
        credential = cursor.fetchone()
        conn.close()
        
        return AppCredentialResponse(**dict(credential))
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="App username already exists")

@app.get("/admin/credentials", response_model=List[AppCredentialResponse], tags=["Admin"])
async def list_credentials():
    """List all app credentials (admin endpoint - should be protected in production)"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, app_username, is_active, created_at FROM app_credentials')
    credentials = cursor.fetchall()
    conn.close()
    
    return [AppCredentialResponse(**dict(cred)) for cred in credentials]

@app.get("/admin/credentials/{credential_id}", response_model=AppCredentialResponse, tags=["Admin"])
async def get_credential(credential_id: int):
    """Get specific app credential"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, app_username, is_active, created_at FROM app_credentials WHERE id = ?', (credential_id,))
    credential = cursor.fetchone()
    conn.close()
    
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    return AppCredentialResponse(**dict(credential))

@app.put("/admin/credentials/{credential_id}/toggle", response_model=AppCredentialResponse, tags=["Admin"])
async def toggle_credential(credential_id: int):
    """Enable or disable an app credential"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM app_credentials WHERE id = ?', (credential_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Credential not found")
    
    cursor.execute('''
        UPDATE app_credentials 
        SET is_active = NOT is_active 
        WHERE id = ?
    ''', (credential_id,))
    conn.commit()
    
    cursor.execute('SELECT id, app_username, is_active, created_at FROM app_credentials WHERE id = ?', (credential_id,))
    credential = cursor.fetchone()
    conn.close()
    
    return AppCredentialResponse(**dict(credential))

@app.delete("/admin/credentials/{credential_id}", tags=["Admin"])
async def delete_credential(credential_id: int):
    """Delete an app credential"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM app_credentials WHERE id = ?', (credential_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Credential not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Credential deleted successfully"}

@app.get("/", tags=["Health"])
async def root():
    """API health check"""
    return {
        "status": "healthy",
        "message": "AI Study Tool API is running",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)