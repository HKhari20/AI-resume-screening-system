import unittest
import time
import json
from app import app, models_loaded, summarizer, embedder, model_lock
import utils

class TestResumeScreener(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        print("Waiting for models to load in test environment...")
        import app as app_module
        # Wait up to 30 seconds for background thread to load models
        start = time.time()
        while time.time() - start < 30:
            if app_module.models_loaded:
                break
            time.sleep(1)
        if not app_module.models_loaded:
            print("Explicitly loading models for test...")
            s, e = utils.load_models()
            with app_module.model_lock:
                app_module.summarizer = s
                app_module.embedder = e
                app_module.models_loaded = True

    def test_01_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"NeuralScreen AI", response.data)
        print("PASS: Index page rendered successfully")

    def test_02_api_status(self):
        response = self.client.get('/api/status')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['models_ready'])
        self.assertIn('preset_jds', data)
        self.assertIn('sample_resumes', data)
        self.assertGreater(len(data['sample_resumes']), 0)
        print(f"PASS: Status endpoint working with {len(data['sample_resumes'])} sample resumes")

    def test_03_analyze_endpoint_with_samples(self):
        jd = "Seeking Senior Machine Learning Engineer with deep PyTorch, Transformers, Hugging Face, and FAISS experience."
        response = self.client.post('/api/analyze', data={
            'job_description': jd,
            'min_score': 30,
            'use_samples': 'true'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        candidates = data['candidates']
        self.assertGreaterEqual(len(candidates), 1)
        
        top_cand = candidates[0]
        print(f"PASS: Top candidate ranked: {top_cand['candidate_name']} with {top_cand['score']}% match")
        self.assertIn('score', top_cand)
        self.assertIn('summary', top_cand)
        self.assertIn('matched_skills', top_cand)

if __name__ == '__main__':
    unittest.main()
