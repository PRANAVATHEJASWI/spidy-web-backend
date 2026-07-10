import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase if variables are available
db = None
is_firebase_configured = False

try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    firebase_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
    firebase_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

    cred = None
    if firebase_json:
        try:
            cred_dict = json.loads(firebase_json)
            cred = credentials.Certificate(cred_dict)
            logger.info("Initializing Firebase using FIREBASE_CREDENTIALS_JSON from environment.")
        except Exception as je:
            logger.error(f"Failed to parse FIREBASE_CREDENTIALS_JSON: {je}")

    elif firebase_path and os.path.exists(firebase_path):
        cred = credentials.Certificate(firebase_path)
        logger.info(f"Initializing Firebase using service account key file at: {firebase_path}")

    if cred:
        # Check if already initialized to avoid duplicate app errors
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        is_firebase_configured = True
        logger.info("Firebase Firestore client initialized successfully!")
    else:
        logger.warning("Firebase credentials not supplied or file does not exist. Falling back to local storage.")

except Exception as e:
    logger.error(f"Error initializing Firebase SDK: {e}. Falling back to local storage.")
    db = None
    is_firebase_configured = False


# --- LOCAL FALLBACK FILE PATHS ---
LOCAL_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local_data")
RESUME_FILE = os.path.join(LOCAL_DATA_DIR, "resume.json")
BLOGS_FILE = os.path.join(LOCAL_DATA_DIR, "blogs.json")

# Ensure local data directory exists
os.makedirs(LOCAL_DATA_DIR, exist_ok=True)

# Default resume structure based on the user's PDF/OCR
DEFAULT_RESUME = {
    "name": "Pranava Thejaswi N M",
    "title": "QA Engineer",
    "subTitle": "Software Engineer • Azentio",
    "description": "Detail-oriented QA Engineer and software developer with experience in scalable test automation, AI-driven systems, and cross-platform application development.",
    "contact": {
        "phone": "7676037294",
        "email": "pranavathejaswi8@gmail.com",
        "linkedin": "https://linkedin.com/in/pranavathejaswi",
        "github": "https://github.com/pranavathejaswi",
        "portfolio": "https://pranavathejaswi.dev",
        "extraUrls": [
            {"label": "LeetCode", "url": "https://leetcode.com/pranavathejaswi"}
        ]
    },
    "education": [
        {
            "institution": "Vidyavardhaka College of Engineering",
            "degree": "Bachelor of Engineering",
            "cgpa": "8.91",
            "duration": "2021 – 2025",
            "link": ""
        }
    ],
    "experience": [
        {
            "role": "Trainee Engineer",
            "company": "Azentio",
            "location": "Bengaluru",
            "duration": "Jun 2025 – Present",
            "link": "",
            "highlights": [
                "Designed and enhanced a scalable Playwright (Java) automation framework using TestNG, supporting parallel execution and centralized configuration.",
                "Integrated API and UI automation workflows, improving regression efficiency and increasing test coverage by 30%.",
                "Implemented retry mechanisms and optimized locator strategies, reducing flaky test failures significantly.",
                "Contributed to end-to-end testing in the Lending domain, ensuring high reliability of critical workflows."
            ]
        },
        {
            "role": "Software Developer Intern",
            "company": "DigitalShark",
            "location": "Bengaluru",
            "duration": "Feb 2025 – Apr 2025",
            "link": "",
            "highlights": [
                "Developed 3+ Qt-based applications including a CSV-to-SQL converter, reducing manual conversion effort by 70%.",
                "Optimized C++/Qt data-processing modules, improving performance by 25–30%."
            ]
        },
        {
            "role": "ML Intern",
            "company": "Mysuru Consulting Group (MCG)",
            "location": "Mysuru",
            "duration": "Apr 2024 – Jul 2024",
            "link": "",
            "highlights": [
                "Built a text-classification model achieving 92% accuracy, improving categorization efficiency by 40%.",
                "Developed a real-time TODO application using Firebase for authentication and cloud synchronization."
            ]
        },
        {
            "role": "Peer Trainer",
            "company": "Vidyavardhaka College of Engineering",
            "location": "Mysuru",
            "duration": "2024",
            "link": "",
            "highlights": [
                "Delivered 36 hours of training on DSA and OOP concepts to undergraduate students."
            ]
        }
    ],
    "projects": [
        {
            "title": "Proctoring System with AI-Driven Automated Exam Management",
            "techStack": "Flask, OpenCV, MediaPipe, YOLO, Dlib, Whisper, Firebase, Generative AI, Flask-Mail",
            "link": "",
            "highlights": [
                "Developed a Flask-based proctoring platform processing 120+ real-time video streams with face/eye tracking and YOLO-based object detection.",
                "Improved cheating detection accuracy to 94% using MediaPipe + Dlib + YOLO integration."
            ]
        }
    ],
    "skills": {
        "languages": ["Java", "Python", "C/C++", "JavaScript", "SQL"],
        "automationTesting": ["Playwright (Java)", "TestNG", "API Testing"],
        "aiLlm": ["RAG (Retrieval-Augmented Generation)", "Prompt Engineering", "LLM Integration"],
        "toolsTechnologies": ["Git", "Maven", "Firebase", "Qt/QML", "Streamlit", "FastAPI", "React"]
    },
    "certificates": [
        "Google Cloud Platform – Data Engineer Learning Path",
        "Google Cloud Platform – Data Analyst Learning Path"
    ],
    "publications": [
        {
            "title": "Comprehensive Proctoring System with AI-Driven Automated Exam Management",
            "journal": "International Journal of Advance Computational Engineering and Networking (IJACEN)",
            "volumeInfo": "Volume-13, Issue-5, 2025",
            "url": "#"
        }
    ],
    "customSections": [
        {
            "title": "Volunteering",
            "items": [
                {"text": "NSS Volunteer – Organized blood donation drives and campus cleaning events.", "link": ""}
            ]
        }
    ],
    "askMrNoob": {
        "enabled": False,
        "label": "Ask MrNoob",
        "disabledMessage": "AI assistant is under construction. Stay tuned!"
    }
}

DEFAULT_BLOGS = [
    {
        "id": "intro-to-playwright",
        "title": "Building Scalable Test Suites with Playwright Java & TestNG",
        "excerpt": "A deep dive into setting up a robust, parallel-executing automation framework from scratch using Playwright's Java binding.",
        "content": "### Introduction\n\nPlaywright has emerged as a powerful tool for modern web testing. In this article, we explore how to combine Playwright's Java API with the TestNG framework to achieve highly reliable, parallel test execution. We will cover locator strategies, handling flaky tests with retry mechanisms, and organizing tests for CI/CD integrations.\n\n### Why Playwright Java?\n\nWhile Node.js is the most common language binding for Playwright, Java provides solid integration with enterprise test-runners like TestNG and JUnit, and is widely used in QA automation teams. Combining the speed of Playwright with the test organization capabilities of TestNG makes for a highly robust combination.",
        "date": "2026-07-01"
    },
    {
        "id": "ai-exam-proctoring",
        "title": "Designing an AI-Driven Proctoring System using OpenCV and YOLO",
        "excerpt": "Exploring the architecture of a real-time exam monitoring system capable of detecting multiple streams and tracking face/eye movement.",
        "content": "### The Challenge of Remote Proctoring\n\nRemote examinations require reliable proctoring interfaces to verify candidate identity and integrity. By leveraging computer vision and deep learning models, we can automate the detection of behavior cues.\n\n### Tech Stack & Architecture\n\nOur system uses: \n- **Flask** for backend video streaming.\n- **OpenCV & MediaPipe** for eye tracking and facial landmarks.\n- **YOLO (You Only Look Once)** to identify objects like mobile phones or additional books in the camera frame.",
        "date": "2026-06-15"
    }
]

# Ensure files exist with default content
if not os.path.exists(RESUME_FILE):
    with open(RESUME_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_RESUME, f, indent=2)

if not os.path.exists(BLOGS_FILE):
    with open(BLOGS_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_BLOGS, f, indent=2)


# --- DATABASE DATABASE INTERFACE FUNCTIONS ---

def get_resume():
    if is_firebase_configured and db:
        try:
            doc_ref = db.collection("resume").document("default")
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            else:
                # Seed database with default resume
                doc_ref.set(DEFAULT_RESUME)
                return DEFAULT_RESUME
        except Exception as e:
            logger.error(f"Error fetching resume from Firestore: {e}")
            # fall through to local
    
    # Local fallback
    try:
        with open(RESUME_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading local resume: {e}")
        return DEFAULT_RESUME


def save_resume(data: dict):
    if is_firebase_configured and db:
        try:
            doc_ref = db.collection("resume").document("default")
            doc_ref.set(data)
            return True
        except Exception as e:
            logger.error(f"Error saving resume to Firestore: {e}")
            raise e
            
    # Local fallback
    try:
        with open(RESUME_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error writing local resume: {e}")
        return False


def get_blogs():
    if is_firebase_configured and db:
        try:
            blogs_ref = db.collection("blogs")
            docs = blogs_ref.stream()
            blogs_list = []
            for doc in docs:
                blog_data = doc.to_dict()
                blog_data["id"] = doc.id
                blogs_list.append(blog_data)
            
            # If firebase is empty, seed it
            if not blogs_list:
                for b in DEFAULT_BLOGS:
                    # extract id from dictionary to use as doc id
                    b_id = b["id"]
                    b_copy = b.copy()
                    del b_copy["id"]
                    db.collection("blogs").document(b_id).set(b_copy)
                    b_copy["id"] = b_id
                    blogs_list.append(b_copy)
            return sorted(blogs_list, key=lambda x: x.get("date", ""), reverse=True)
        except Exception as e:
            logger.error(f"Error streaming blogs from Firestore: {e}")
            # fall through to local

    # Local fallback
    try:
        with open(BLOGS_FILE, "r", encoding="utf-8") as f:
            blogs = json.load(f)
            return sorted(blogs, key=lambda x: x.get("date", ""), reverse=True)
    except Exception as e:
        logger.error(f"Error reading local blogs: {e}")
        return DEFAULT_BLOGS


def get_blog(blog_id: str):
    if is_firebase_configured and db:
        try:
            doc_ref = db.collection("blogs").document(blog_id)
            doc = doc_ref.get()
            if doc.exists:
                blog_data = doc.to_dict()
                blog_data["id"] = doc.id
                return blog_data
        except Exception as e:
            logger.error(f"Error getting blog {blog_id} from Firestore: {e}")
            # fall through to local
            
    # Local fallback
    blogs = get_blogs()
    for blog in blogs:
        if blog.get("id") == blog_id:
            return blog
    return None


def save_blog(blog_id: str, data: dict):
    # Ensure ID is not inside data dictionary saved in Firebase (Firestore handles IDs as doc ids)
    data_to_save = data.copy()
    if "id" in data_to_save:
        del data_to_save["id"]

    if is_firebase_configured and db:
        try:
            doc_ref = db.collection("blogs").document(blog_id)
            doc_ref.set(data_to_save)
            return True
        except Exception as e:
            logger.error(f"Error saving blog to Firestore: {e}")
            raise e

    # Local fallback
    try:
        blogs = get_blogs()
        updated_blogs = []
        found = False
        for b in blogs:
            if b.get("id") == blog_id:
                # Merge new values
                merged = {**b, **data}
                merged["id"] = blog_id
                updated_blogs.append(merged)
                found = True
            else:
                updated_blogs.append(b)
        
        if not found:
            # Create new
            new_blog = data.copy()
            new_blog["id"] = blog_id
            updated_blogs.append(new_blog)

        with open(BLOGS_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_blogs, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error writing local blogs: {e}")
        return False


def delete_blog(blog_id: str):
    if is_firebase_configured and db:
        try:
            db.collection("blogs").document(blog_id).delete()
            return True
        except Exception as e:
            logger.error(f"Error deleting blog {blog_id} from Firestore: {e}")
            raise e

    # Local fallback
    try:
        blogs = get_blogs()
        updated_blogs = [b for b in blogs if b.get("id") != blog_id]
        with open(BLOGS_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_blogs, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error writing local blogs: {e}")
        return False
