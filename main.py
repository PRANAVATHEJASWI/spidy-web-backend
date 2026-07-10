import os
import uvicorn
from fastapi import FastAPI, HTTPException, Header, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import database

app = FastAPI(title="Pranava Thejaswi - Portfolio Backend", version="1.0.0")

# CORS Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "")
origins = [o.strip() for o in ALLOWED_ORIGINS.split(",") if o.strip()] if ALLOWED_ORIGINS else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Access tokens from environment
EDITOR_ACCESS_TOKEN = os.getenv("EDITOR_ACCESS_TOKEN", "")
READONLY_ACCESS_TOKEN = os.getenv("READONLY_ACCESS_TOKEN", "")

def get_token_role(authorization: Optional[str]) -> str:
    if not EDITOR_ACCESS_TOKEN and not READONLY_ACCESS_TOKEN:
        return "editor" # No auth configured, default to editor
    
    if not authorization:
        return "none"
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return "none"
        
    token = parts[1]
    if EDITOR_ACCESS_TOKEN and token == EDITOR_ACCESS_TOKEN:
        return "editor"
    if READONLY_ACCESS_TOKEN and token == READONLY_ACCESS_TOKEN:
        return "readonly"
        
    return "none"

def verify_editor_token(authorization: Optional[str] = Header(None)):
    role = get_token_role(authorization)
    if role == "none":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing access token"
        )
    if role == "readonly":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Read-only token cannot modify data"
        )

# --- PYDANTIC MODEL SCHEMAS ---

class ContactSchema(BaseModel):
    phone: str
    email: str
    linkedin: str
    github: str
    portfolio: str
    extraUrls: List[Dict[str, str]] = []

class EducationItem(BaseModel):
    institution: str
    degree: str
    cgpa: str
    duration: str
    link: Optional[str] = ""

class ExperienceItem(BaseModel):
    role: str
    company: str
    location: str
    duration: str
    highlights: List[str]
    link: Optional[str] = ""

class ProjectItem(BaseModel):
    title: str
    techStack: str
    highlights: List[str]
    link: Optional[str] = ""

class SkillsSchema(BaseModel):
    languages: List[str]
    automationTesting: List[str]
    aiLlm: List[str]
    toolsTechnologies: List[str]

class PublicationItem(BaseModel):
    title: str
    journal: str
    volumeInfo: str
    url: str

class CustomSectionItemSchema(BaseModel):
    text: str
    link: Optional[str] = ""

class CustomSectionSchema(BaseModel):
    title: str
    type: str = "list"
    items: List[CustomSectionItemSchema]

class AskMrNoobSchema(BaseModel):
    enabled: bool
    label: str
    disabledMessage: str

class ResumeSchema(BaseModel):
    name: str
    title: str
    subTitle: str
    description: str = ""
    contact: ContactSchema
    education: List[EducationItem]
    experience: List[ExperienceItem]
    projects: List[ProjectItem]
    skills: SkillsSchema
    certificates: List[str]
    publications: List[PublicationItem]
    customSections: List[CustomSectionSchema] = []
    askMrNoob: AskMrNoobSchema = Field(default_factory=lambda: {"enabled": False, "label": "Ask MrNoob", "disabledMessage": "AI assistant is under construction."})


class BlogCreateSchema(BaseModel):
    title: str
    excerpt: str
    content: str
    date: str

class BlogSchema(BlogCreateSchema):
    id: str


# --- API ENDPOINTS ---

@app.head("/")
def head_root():
    """Handle HEAD requests for uptime monitoring."""
    return {}
    
@app.get("/api/status")
def get_status():
    return {
        "status": "online",
        "firebase_connected": database.is_firebase_configured,
        "auth_enabled": bool(EDITOR_ACCESS_TOKEN or READONLY_ACCESS_TOKEN)
    }

@app.get("/api/auth/verify")
def verify_auth_token_endpoint(authorization: Optional[str] = Header(None)):
    role = get_token_role(authorization)
    return {"role": role}

# --- RESUME ROUTES ---

@app.get("/api/resume", response_model=ResumeSchema)
def get_resume():
    try:
        return database.get_resume()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch resume: {str(e)}"
        )

@app.post("/api/resume")
def update_resume(resume_data: ResumeSchema, _auth=Depends(verify_editor_token)):
    try:
        success = database.save_resume(resume_data.model_dump())
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save resume"
            )
        return {"message": "Resume updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update resume: {str(e)}"
        )


# --- BLOG ROUTES ---

@app.get("/api/blogs", response_model=List[BlogSchema])
def get_blogs():
    try:
        return database.get_blogs()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch blogs: {str(e)}"
        )

@app.get("/api/blogs/{blog_id}", response_model=BlogSchema)
def get_blog(blog_id: str):
    blog = database.get_blog(blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with ID {blog_id} not found"
        )
    return blog

@app.post("/api/blogs", response_model=BlogSchema)
def create_blog(blog_data: BlogCreateSchema, _auth=Depends(verify_editor_token)):
    try:
        # Create an ID from the title (slugify)
        blog_id = blog_data.title.lower().replace(" ", "-")
        # Ensure only alphanumeric and dashes
        blog_id = "".join(c for c in blog_id if c.isalnum() or c == "-")
        
        # Check if already exists, append unique suffix if needed
        existing = database.get_blog(blog_id)
        if existing:
            import time
            blog_id = f"{blog_id}-{int(time.time())}"
            
        full_blog = blog_data.model_dump()
        full_blog["id"] = blog_id
        
        success = database.save_blog(blog_id, full_blog)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create blog"
            )
        return full_blog
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create blog: {str(e)}"
        )

@app.put("/api/blogs/{blog_id}", response_model=BlogSchema)
def update_blog(blog_id: str, blog_data: BlogCreateSchema, _auth=Depends(verify_editor_token)):
    existing = database.get_blog(blog_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with ID {blog_id} not found"
        )
    try:
        full_blog = blog_data.model_dump()
        full_blog["id"] = blog_id
        
        success = database.save_blog(blog_id, full_blog)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update blog"
            )
        return full_blog
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update blog: {str(e)}"
        )

@app.delete("/api/blogs/{blog_id}")
def delete_blog(blog_id: str, _auth=Depends(verify_editor_token)):
    existing = database.get_blog(blog_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with ID {blog_id} not found"
        )
    try:
        success = database.delete_blog(blog_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete blog"
            )
        return {"message": f"Blog with ID {blog_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete blog: {str(e)}"
        )


# --- SERVE FRONTEND STATIC FILES (Production) ---
# In production, the built frontend (dist/) is copied into ./static/
# The backend serves it directly — no separate frontend server needed.

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

if os.path.isdir(STATIC_DIR):
    # Serve static assets (JS, CSS, images) under /assets
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="static-assets")

    # Catch-all: serve index.html for any non-API route (SPA routing)
    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        # If the file exists in static dir, serve it directly
        file_path = os.path.join(STATIC_DIR, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        # Otherwise serve index.html for SPA client-side routing
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    uvicorn.run("main:app", host=host, port=port, reload=True)
