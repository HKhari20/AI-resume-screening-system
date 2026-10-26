import streamlit as st
import utils
import pandas as pd
import numpy as np

# Configure Streamlit page
st.set_page_config(page_title="AI Resume Screener", page_icon="🔮", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for a beautiful futuristic/glassmorphism look
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #e2e8f0;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00ffcc !important;
        font-family: 'Courier New', Courier, monospace;
        letter-spacing: 1px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(0, 255, 204, 0.2);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #00ffcc 0%, #3b82f6 100%);
        color: #000000 !important;
        font-weight: 800;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(0, 255, 204, 0.4);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 25px rgba(0, 255, 204, 0.6);
        color: #ffffff !important;
    }
    
    /* Cards and Dataframes */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid rgba(0, 255, 204, 0.2);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.7) !important;
        color: #00ffcc !important;
        border-radius: 5px;
        border: 1px solid rgba(0, 255, 204, 0.2);
    }
    
    /* Custom Match Score styling */
    .score-high { color: #00ffcc; font-weight: bold; font-size: 1.2rem; }
    .score-med { color: #fbbf24; font-weight: bold; font-size: 1.2rem; }
    .score-low { color: #ef4444; font-weight: bold; font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://huggingface.co/front/assets/huggingface_logo-noborder.svg", width=50)
    st.title("Settings & Info")
    st.markdown("This system runs **100% locally** on your machine. No data is sent to external APIs.")
    st.divider()
    st.markdown("### 🧠 AI Models")
    st.markdown("- **Summarizer:** `t5-small`")
    st.markdown("- **Embeddings:** `all-MiniLM-L6-v2`")
    st.markdown("- **Search:** `FAISS (Cosine)`")
    st.divider()
    st.markdown("### ⚙️ Thresholds")
    min_score = st.slider("Minimum Match %", 0, 100, 40)

# --- MAIN UI ---
st.title("🔮 AI Resume Screening & Matcher")
st.markdown("*Futuristic HR Intelligence Powered by Hugging Face*")
st.markdown("---")

@st.cache_resource(show_spinner=False)
def init_models():
    return utils.load_models()

with st.spinner("Initializing Neural Networks... 🤖"):
    summarizer, embedder = init_models()

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("🎯 Target Profile")
    job_desc = st.text_area("Job Description / Required Skills", height=200, placeholder="E.g., Senior Python developer with expertise in Machine Learning, Pandas, and Neural Networks...")

with col2:
    st.subheader("📂 Candidate Resumes")
    uploaded_files = st.file_uploader("Upload PDF Resumes", type="pdf", accept_multiple_files=True)

st.write("")
analyze_btn = st.button("🚀 INITIATE AI ANALYSIS", use_container_width=True)

if analyze_btn:
    if not job_desc:
        st.error("⚠️ Please define a target job description.")
    elif not uploaded_files:
        st.error("⚠️ Please upload at least one candidate resume.")
    else:
        with st.status("🧠 Processing Candidates...", expanded=True) as status:
            resume_data = []
            resume_texts = []
            
            st.write("Extracting and reading documents...")
            for file in uploaded_files:
                text = utils.extract_text_from_pdf(file)
                if not text.strip():
                    st.warning(f"Could not extract text from {file.name}")
                    continue
                
                st.write(f"Generating AI summary for {file.name}...")
                summary = utils.summarize_text(summarizer, text)
                resume_data.append({
                    "Filename": file.name, 
                    "Summary": summary, 
                    "OriginalText": text
                })
                resume_texts.append(summary) 
            
            if resume_texts:
                st.write("Vectorizing profiles into semantic space...")
                jd_embedding = utils.embed_texts(embedder, [job_desc]).astype(np.float32)
                resume_embeddings = utils.embed_texts(embedder, resume_texts).astype(np.float32)
                
                st.write("Executing FAISS Semantic Search...")
                index = utils.create_faiss_index(resume_embeddings)
                
                k = min(len(resume_texts), 10)
                similarities, indices = utils.semantic_search(index, jd_embedding, k)
                
                status.update(label="✅ Analysis Complete!", state="complete", expanded=False)
                
                st.markdown("## 🏆 Top Candidates")
                
                # Display Results in a visually appealing way
                for i, idx in enumerate(indices[0]):
                    if idx < len(resume_data) and idx != -1:
                        sim = similarities[0][i]
                        score = max(0, sim * 100) # Convert to percentage
                        
                        if score >= min_score:
                            with st.container():
                                col_rank, col_info, col_score = st.columns([1, 6, 2])
                                
                                with col_rank:
                                    st.markdown(f"## #{i+1}")
                                
                                with col_info:
                                    st.markdown(f"**{resume_data[idx]['Filename']}**")
                                    with st.expander("View AI Summary"):
                                        st.info(resume_data[idx]['Summary'])
                                        
                                with col_score:
                                    if score > 75:
                                        st.markdown(f"<div class='score-high'>{score:.1f}% MATCH</div>", unsafe_allow_html=True)
                                        st.progress(score / 100.0)
                                    elif score > 50:
                                        st.markdown(f"<div class='score-med'>{score:.1f}% MATCH</div>", unsafe_allow_html=True)
                                        st.progress(score / 100.0)
                                    else:
                                        st.markdown(f"<div class='score-low'>{score:.1f}% MATCH</div>", unsafe_allow_html=True)
                                        st.progress(score / 100.0)
                                st.divider()
                
            else:
                status.update(label="❌ Failed to extract text.", state="error")

