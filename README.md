# 🚀 NeuralScreen AI - Local Resume Screening & Semantic Matcher

A cutting-edge, vibrant web application built with **Flask**, **Tailwind CSS**, and **Hugging Face Transformers** for automated recruitment intelligence and resume screening.

This system runs **100% locally** on your machine—ensuring candidate confidentiality without sending any sensitive resume data to external cloud APIs.

---

## 🌟 Key Highlights & Features

- 🎨 **Vibrant Cyber-Luminescent UI**: Modern dark glassmorphism dashboard with glowing radial progress meters, animated status indicators, and smooth micro-interactions.
- ⚡ **Hugging Face T5 Summarization**: Standardizes noisy resumes into clean, high-signal executive summaries using the `t5-small` sequence-to-sequence model.
- 🎯 **Semantic Vector Matching**: Maps job profiles and candidate summaries into 384-dimensional dense vectors using `all-MiniLM-L6-v2`.
- 🔍 **Meta FAISS Vector Search**: Instantaneous cosine similarity calculation and candidate ranking using Facebook AI Similarity Search (`faiss-cpu`).
- 🏷️ **Skill Gap Extraction**: Automatically detects technical skills, highlights matched criteria, and flags missing qualifications from the job description.
- 📂 **Multi-Format Ingestion**: Drag-and-drop support for PDF, TXT, and Markdown documents.
- 🧪 **1-Click Preloaded Testing**: Includes 4 realistic sample resumes and instant Job Description presets (ML Engineer, Full Stack, Data Analyst, DevOps) so you can test immediately with zero setup.
- 📊 **Dual Views & Export**: Toggle between interactive Card Grid and Comparison Table views, and export full rankings to **CSV** or **JSON**.

---

## 🛠️ Architecture & Tech Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | Flask (Python 3.9+) |
| **Document Processing** | PyPDF2 |
| **Neural Summarizer** | Hugging Face `transformers` (`t5-small`) |
| **Semantic Embeddings** | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| **Vector Engine** | Meta `faiss-cpu` (Inner Product / Cosine Similarity) |
| **Frontend UI** | HTML5, Tailwind CSS, Lucide Icons, Glassmorphism CSS |
| **Export Formats** | CSV Spreadsheet & Structured JSON |

---

## 🚀 Quick Start Guide

### 1. Launch with One Click (Windows)
Double-click `run.bat` in the project root:
```bash
run.bat
```
This script will:
1. Activate the Python virtual environment (`venv`).
2. Verify all required dependencies.
3. Automatically open your browser at `http://127.0.0.1:5000`.
4. Launch the Flask application.

### 2. Manual Launch
```bash
# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py
```
Open **`http://127.0.0.1:5000`** in your browser.

---

## 🧪 Quick Test Drive (No Resumes Needed)

1. Click any **Quick 1-Click Preset** (e.g., `⚡ ML / NLP Engineer`).
2. Click **`⚡ Load Sample Resumes`** in the candidate upload panel.
3. Click **`🚀 INITIATE NEURAL SCREENING & RANKING`**.
4. Watch the 4-stage neural pipeline analyze the candidates, generate T5 summaries, compute vector embeddings, and rank candidates with real-time radial gauges!

---

## 📁 Project Structure

```
resume_screening_system/
│
├── app.py                     # Main Flask web application & REST API
├── app_streamlit.py           # Preserved backup of original Streamlit version
├── utils.py                   # Core neural pipeline (T5, MiniLM, FAISS, PDF parsing)
├── generate_samples.py        # Generates sample PDF resumes
├── test_app.py                # Automated end-to-end integration test suite
├── requirements.txt           # Python dependencies
├── run.bat                    # One-click Windows launch script
│
├── sample_resumes/            # Pre-generated candidate resumes
│   ├── Alex_Rivera_Senior_ML_Engineer.pdf
│   ├── Sarah_Chen_Full_Stack_Dev.pdf
│   ├── Michael_Kumar_Data_Analyst.pdf
│   └── Emily_Taylor_DevOps_Cloud.pdf
│
├── templates/
│   └── index.html             # Futuristic glassmorphism dashboard
│
└── static/
    ├── css/
    │   └── custom.css         # Cyberpunk animations, glowing meters, scrollbars
    └── js/
        └── app.js             # Drag & drop, real-time filtering, exports, modals
```

---

## 🔒 Privacy & Security

All AI models (`t5-small` and `all-MiniLM-L6-v2`) run completely on your local CPU/GPU. No candidate data, resumes, or job descriptions are transmitted over the internet.
