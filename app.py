import os
import time
import threading
import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory
import utils

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

# Global model state
models_loaded = False
loading_error = None
summarizer = None
embedder = None
model_lock = threading.Lock()

def initialize_models_background():
    global summarizer, embedder, models_loaded, loading_error
    try:
        print("[STARTUP] Initializing AI Models in background thread...")
        s, e = utils.load_models()
        with model_lock:
            summarizer = s
            embedder = e
            models_loaded = True
        print("[STARTUP] AI Models successfully loaded into memory!")
    except Exception as exc:
        print(f"[STARTUP ERROR] Failed to load models: {exc}")
        loading_error = str(exc)

# Start model loading immediately in background thread so app boots quickly
threading.Thread(target=initialize_models_background, daemon=True).start()

SAMPLE_RESUMES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_resumes")

PRESET_JDS = {
    "ml_engineer": {
        "title": "Senior Machine Learning & NLP Engineer",
        "description": "We are seeking a Senior Machine Learning Engineer with 4+ years experience in Natural Language Processing (NLP), Transformers, Hugging Face ecosystem, and PyTorch. The ideal candidate has deep hands-on expertise building vector search systems using FAISS or Milvus, fine-tuning large language models (LLMs), and deploying containerized inference pipelines on AWS or GCP using Docker and Kubernetes."
    },
    "full_stack": {
        "title": "Senior Full-Stack Developer",
        "description": "Looking for an experienced Full-Stack Engineer skilled in TypeScript, React, Next.js, and Node.js. Experience designing scalable relational databases with PostgreSQL, developing clean REST and GraphQL APIs, and writing automated tests with Jest is required. Exposure to Tailwind CSS and Docker is a strong plus."
    },
    "data_analyst": {
        "title": "Lead Data Analyst & BI Specialist",
        "description": "Seeking a Senior Data Analyst proficient in SQL, Python (Pandas, NumPy), and business intelligence visualization tools like Tableau and Power BI. The role involves data warehousing with Snowflake or BigQuery, statistical modeling, A/B testing analysis, and building executive financial and operational dashboards."
    },
    "devops_engineer": {
        "title": "Cloud DevOps & Infrastructure Engineer",
        "description": "Seeking an Infrastructure / DevOps Engineer with deep expertise in AWS cloud services, Terraform Infrastructure as Code (IaC), Kubernetes cluster administration, and automated CI/CD pipelines via GitHub Actions. Strong background in Linux systems, Prometheus monitoring, and container security is required."
    }
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status", methods=["GET"])
def get_status():
    samples = []
    if os.path.exists(SAMPLE_RESUMES_DIR):
        samples = [f for f in os.listdir(SAMPLE_RESUMES_DIR) if f.endswith(".pdf")]
    
    return jsonify({
        "models_ready": models_loaded,
        "loading_error": loading_error,
        "sample_resumes": samples,
        "preset_jds": PRESET_JDS
    })

@app.route("/sample_resumes/<filename>")
def download_sample_resume(filename):
    return send_from_directory(SAMPLE_RESUMES_DIR, filename)

@app.route("/api/analyze", methods=["POST"])
def analyze_resumes():
    global summarizer, embedder, models_loaded
    
    if not models_loaded:
        return jsonify({
            "success": False,
            "error": "AI models are still initializing in the background. Please wait a few seconds and try again."
        }), 503

    start_time = time.time()
    
    job_desc = request.form.get("job_description", "").strip()
    if not job_desc:
        return jsonify({"success": False, "error": "Please provide a job description."}), 400

    min_score = float(request.form.get("min_score", 40.0))
    use_samples = request.form.get("use_samples", "false").lower() == "true"
    
    resumes_to_process = []
    
    if use_samples:
        if os.path.exists(SAMPLE_RESUMES_DIR):
            for fname in os.listdir(SAMPLE_RESUMES_DIR):
                if fname.endswith(".pdf"):
                    fpath = os.path.join(SAMPLE_RESUMES_DIR, fname)
                    with open(fpath, "rb") as f:
                        content = f.read()
                    resumes_to_process.append({"filename": fname, "content": content})
    else:
        uploaded_files = request.files.getlist("resumes")
        for file in uploaded_files:
            if file and file.filename:
                content = file.read()
                if content:
                    resumes_to_process.append({"filename": file.filename, "content": content})
                    
    if not resumes_to_process:
        return jsonify({"success": False, "error": "Please upload at least one resume or select sample resumes."}), 400

    # Step 1: Text extraction & metadata extraction
    processed_candidates = []
    summaries = []
    
    for item in resumes_to_process:
        filename = item["filename"]
        content = item["content"]
        
        raw_text = utils.extract_text_from_file(content, filename)
        if not raw_text.strip():
            continue
            
        metadata = utils.extract_metadata(raw_text, filename)
        skill_analysis = utils.analyze_skill_match(metadata["skills"], job_desc)
        
        # Step 2: T5 Summarization
        summary = utils.summarize_text(summarizer, raw_text)
        summaries.append(summary)
        
        preview = raw_text[:600] + ("..." if len(raw_text) > 600 else "")
        
        processed_candidates.append({
            "filename": filename,
            "candidate_name": metadata["candidate_name"],
            "email": metadata["email"],
            "phone": metadata["phone"],
            "skills": metadata["skills"],
            "matched_skills": skill_analysis["matched_skills"],
            "missing_skills": skill_analysis["missing_skills"],
            "summary": summary,
            "preview_text": preview,
            "raw_length": len(raw_text)
        })

    if not processed_candidates:
        return jsonify({"success": False, "error": "Could not extract readable text from any uploaded resumes."}), 400

    # Step 3: Semantic Vector Embeddings
    jd_embedding = utils.embed_texts(embedder, [job_desc]).astype(np.float32)
    candidate_embeddings = utils.embed_texts(embedder, summaries).astype(np.float32)
    
    # Step 4: FAISS Vector Index & Search
    index = utils.create_faiss_index(candidate_embeddings)
    k = len(processed_candidates)
    similarities, indices = utils.semantic_search(index, jd_embedding, k=k)
    
    # Step 5: Rank & assemble results
    ranked_results = []
    for rank_idx, cand_idx in enumerate(indices[0]):
        if cand_idx < len(processed_candidates) and cand_idx != -1:
            sim = float(similarities[0][rank_idx])
            score = round(max(0.0, sim * 100.0), 1)
            
            cand_data = processed_candidates[cand_idx].copy()
            cand_data["rank"] = rank_idx + 1
            cand_data["similarity"] = sim
            cand_data["score"] = score
            
            if score >= 75:
                cand_data["tier"] = "high"
                cand_data["tier_label"] = "High Match"
            elif score >= 50:
                cand_data["tier"] = "medium"
                cand_data["tier_label"] = "Moderate Match"
            else:
                cand_data["tier"] = "low"
                cand_data["tier_label"] = "Low Match"
                
            cand_data["passes_threshold"] = score >= min_score
            ranked_results.append(cand_data)

    elapsed_time = round(time.time() - start_time, 2)
    
    all_scores = [r["score"] for r in ranked_results]
    stats = {
        "total_screened": len(ranked_results),
        "above_threshold": sum(1 for r in ranked_results if r["passes_threshold"]),
        "highest_score": max(all_scores) if all_scores else 0,
        "average_score": round(sum(all_scores) / len(all_scores), 1) if all_scores else 0,
        "processing_time_sec": elapsed_time
    }
    
    return jsonify({
        "success": True,
        "candidates": ranked_results,
        "stats": stats,
        "min_score": min_score
    })

if __name__ == "__main__":
    print("==================================================================")
    print(" 🚀 AI RESUME SCREENING & MATCHING SYSTEM (FLASK)")
    print(" Local Neural Engine powered by Hugging Face (T5 + MiniLM + FAISS)")
    print(" Open in your browser: http://127.0.0.1:5000")
    print("==================================================================")
    app.run(host="127.0.0.1", port=5000, debug=False)
