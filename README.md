# 🦷 DentAI — Dental X-ray AI Backend

A FastAPI backend that processes dental panoramic X-ray images, runs AI-based pathology detection using YOLOv8, generates SVG polygon overlays for frontend annotation, and produces structured diagnostic reports via an LLM pipeline.

---

## 🧠 Features

- **AI Detection** — YOLOv8-based model detects dental pathologies from panoramic X-ray images
- **Overlay Generation** — Returns bounding box / polygon data for SVG annotation on the frontend
- **Treatment Lookup** — Maps detected class IDs to treatment recommendations
- **Report Generation** — LLM-powered structured diagnostic report generation
- **Annotation Saving** — Persists user-edited annotations to a PostgreSQL database
- **Static Image Export** — Renders a static annotated image for PDF export
- **Security** — File type validation, size limits (10MB), filename sanitization, CORS restricted to frontend origin

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd backend
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://user:password@host:5432/dental_ai_db
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
MODEL_PATH=weights/your_model.pt
OPENAI_API_KEY=your_api_key_here
```

### 4. Set up required folders and files

```bash
mkdir -p uploads outputs weights
```

Then place your trained YOLOv8 weights file inside `weights/`.

### 5. Set up the database

Make sure your PostgreSQL instance is running and accessible via the `DATABASE_URL` in your `.env`.

### 6. Run the server

```bash
uvicorn app:app --reload
```

Server will start at: `http://127.0.0.1:8000`

Interactive API docs available at: `http://127.0.0.1:8000/docs`

---

## 🐳 Docker Setup

If using Docker Compose (recommended for full-stack deployment):

```bash
docker compose up --build
```

Make sure your `docker-compose.yml` sets the correct environment variables and mounts the `weights/` directory.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/overlay-data` | Upload X-ray image → returns detection overlay data |
| `GET` | `/treatment/{class_id}` | Get treatment recommendation for a detected class |
| `POST` | `/generate-report` | Generate LLM diagnostic report for an image |
| `POST` | `/get-static-image` | Render and return a static annotated image |
| `POST` | `/save-annotations` | Save user-edited annotations to the database |

---

## ⚙️ Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `UPLOAD_DIR` | Directory for uploaded X-ray images |
| `OUTPUT_DIR` | Directory for generated output images |
| `MODEL_PATH` | Path to YOLOv8 `.pt` weights file |
| `OPENAI_API_KEY` | API key for LLM report generation |

---

## 🔒 Security Notes

- Only `image/jpeg` and `image/png` files are accepted
- Maximum upload size is **10MB**
- Filenames are sanitized before saving to disk
- CORS is restricted to the frontend origin (`http://localhost:5173`)
- Never commit your `.env` file — it is listed in `.gitignore`

---

## 🛠️ Tech Stack

- **Framework:** FastAPI
- **AI Model:** YOLOv8 (Ultralytics)
- **Database:** PostgreSQL + SQLAlchemy
- **LLM:** Llama 3 via Ollama / OpenAI API
- **Containerization:** Docker
- **Server:** Uvicorn

---

## 👩‍💻 Authors

Developed as a Final Year Project at Saint Joseph University (ESIB), in collaboration with Tomorrow Services.