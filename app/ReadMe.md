# 🦷 Dental X-ray AI Backend

This backend processes dental X-ray images, performs AI-based anomaly detection, generates visual masks, and produces structured medical reports using a large language model.

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd backend
```
### 2. Install dependencies
pip install -r requirements.txt

### 3. Configure environment variables

Create a .env file in the root directory:

```python 
DATABASE_URL=your_database_url_here
UPLOAD_DIR=uploads
MODEL_PATH=weights/your_model_file.pt
```

⚙️ Required Setup Before Running

Before starting the server, make sure you:

📌 Add your trained model weights inside the weights/ folder
📌 Create an outputs/ folder in the root directory (used for generated images)
📌 Ensure your database is properly set up and accessible

▶️ Run the Backend
uvicorn app:app --reload

Server will start at:

http://127.0.0.1:8000