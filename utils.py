import PyPDF2
import io
import re
from transformers import T5Tokenizer, T5ForConditionalGeneration
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import warnings

warnings.filterwarnings("ignore")

# Comprehensive common skill taxonomy for recruitment analysis
COMMON_SKILLS = [
    # Languages
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust", "PHP", "Ruby", "Swift", "Kotlin", "SQL", "R", "Bash", "Shell", "HTML", "CSS",
    # AI & ML
    "Machine Learning", "Deep Learning", "NLP", "Natural Language Processing", "Computer Vision", 
    "Transformers", "Hugging Face", "PyTorch", "TensorFlow", "Keras", "Scikit-Learn", 
    "FAISS", "Sentence-Transformers", "LangChain", "LlamaIndex", "OpenAI", "BERT", "T5", "LLM", "LLMs", "RAG",
    # Data & Analytics
    "Pandas", "NumPy", "SciPy", "Tableau", "Power BI", "Snowflake", "BigQuery", "Data Warehousing", 
    "ETL", "Spark", "Hadoop", "Data Analysis", "Statistics", "A/B Testing",
    # Web & Backend
    "React", "Next.js", "Vue.js", "Angular", "Node.js", "Express", "FastAPI", "Flask", "Django", 
    "REST API", "RESTful", "GraphQL", "Tailwind CSS", "Bootstrap", "Redux", "WebSockets",
    # Databases & Caching
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra", "SQLite", "DynamoDB",
    # DevOps & Cloud
    "AWS", "GCP", "Google Cloud", "Azure", "Docker", "Kubernetes", "Terraform", "CI/CD", 
    "GitHub Actions", "Jenkins", "Linux", "Ansible", "Helm", "Prometheus", "Grafana", "Git",
    # Methodologies & Architecture
    "Microservices", "Agile", "Scrum", "TDD", "System Design", "Cloud Computing"
]

def load_models():
    """Initializes and loads the T5 summarizer and Sentence Transformer models."""
    print("Loading T5 Summarizer (t5-small)...")
    tokenizer = T5Tokenizer.from_pretrained("t5-small")
    model = T5ForConditionalGeneration.from_pretrained("t5-small")
    summarizer = {"tokenizer": tokenizer, "model": model}
    
    print("Loading Sentence Transformer (all-MiniLM-L6-v2)...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    return summarizer, embedder

def extract_text_from_pdf(pdf_file):
    """
    Extracts text from a PDF file.
    Supports file path string, byte streams (BytesIO, SpooledTemporaryFile), or open file handles.
    """
    try:
        if isinstance(pdf_file, (bytes, bytearray)):
            pdf_file = io.BytesIO(pdf_file)
        
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def extract_text_from_file(file_storage, filename=""):
    """
    Extracts text from uploaded file object supporting .pdf, .txt, .md.
    """
    filename_lower = filename.lower()
    try:
        if filename_lower.endswith(".pdf"):
            return extract_text_from_pdf(file_storage)
        elif filename_lower.endswith((".txt", ".md", ".csv")):
            content = file_storage.read()
            if isinstance(content, bytes):
                return content.decode("utf-8", errors="ignore").strip()
            return str(content).strip()
        else:
            # Attempt PDF first, then raw text
            text = extract_text_from_pdf(file_storage)
            if not text:
                try:
                    file_storage.seek(0)
                    content = file_storage.read()
                    if isinstance(content, bytes):
                        return content.decode("utf-8", errors="ignore").strip()
                except Exception:
                    pass
            return text
    except Exception as e:
        print(f"Error extracting text from {filename}: {e}")
        return ""

def extract_metadata(text, filename=""):
    """
    Extracts candidate name, email, phone, and skills from resume text.
    """
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    
    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)
    
    email = emails[0] if emails else "Not specified"
    phone = phones[0] if phones else "Not specified"
    
    # Candidate name extraction: fallback to cleaned filename or first non-empty line
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    candidate_name = ""
    for line in lines[:3]:
        # Avoid lines that look like emails or phone numbers
        if "@" not in line and not any(char.isdigit() for char in line) and len(line) < 50:
            candidate_name = line
            break
            
    if not candidate_name:
        clean_name = re.sub(r'[\-_]', ' ', filename)
        clean_name = re.sub(r'\.[a-zA-Z0-9]+$', '', clean_name)
        candidate_name = clean_name.title()

    # Extract detected skills from our taxonomy
    text_lower = text.lower()
    found_skills = []
    for skill in COMMON_SKILLS:
        # Match as whole word / phrase
        pattern = r'(?<![a-zA-Z0-9])' + re.escape(skill.lower()) + r'(?![a-zA-Z0-9])'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
            
    return {
        "candidate_name": candidate_name,
        "email": email,
        "phone": phone,
        "skills": found_skills
    }

def analyze_skill_match(candidate_skills, jd_text):
    """
    Compares candidate skills against skills required in Job Description.
    """
    jd_lower = jd_text.lower()
    jd_required_skills = []
    
    for skill in COMMON_SKILLS:
        pattern = r'(?<![a-zA-Z0-9])' + re.escape(skill.lower()) + r'(?![a-zA-Z0-9])'
        if re.search(pattern, jd_lower):
            jd_required_skills.append(skill)
            
    matched = [s for s in candidate_skills if s.lower() in [j.lower() for j in jd_required_skills]]
    missing = [s for s in jd_required_skills if s.lower() not in [c.lower() for c in candidate_skills]]
    
    return {
        "jd_skills": jd_required_skills,
        "matched_skills": matched,
        "missing_skills": missing
    }

def summarize_text(summarizer, text, max_length=150):
    """
    Summarizes text using the Hugging Face T5 model.
    """
    if not text.strip():
        return "No text available for summarization."
        
    # Truncate text to avoid model length errors
    text = text[:2000]
    
    tokenizer = summarizer["tokenizer"]
    model = summarizer["model"]
    
    # T5 requires the prefix "summarize: "
    input_text = "summarize: " + text
    input_ids = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True).input_ids
    
    # Generate summary
    outputs = model.generate(input_ids, max_length=max_length, min_length=25, do_sample=False)
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary

def embed_texts(embedder, texts):
    """
    Generates dense embeddings for a list of strings using SentenceTransformer.
    """
    return embedder.encode(texts)

def create_faiss_index(embeddings):
    """
    Creates a FAISS IndexFlatIP (Cosine Similarity after L2 normalization).
    """
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    return index

def semantic_search(index, query_embedding, k=5):
    """
    Performs FAISS semantic search with query embedding.
    """
    faiss.normalize_L2(query_embedding)
    similarities, indices = index.search(query_embedding, k)
    return similarities, indices
