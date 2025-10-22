🍴 SafeBites

A full-stack AI-powered Food Delivery System that combines a React frontend with a FastAPI + Langgraph + MongoDB backend.

🚀 Features

🍽️ Restaurant & Menu Search — Natural language search using Langgraph & FAISS

🤖 AI Query Understanding — Extracts user intents and applies structured filters

💾 MongoDB Integration — Manages restaurants, dishes, and user profiles

⚡ FastAPI Backend — Modular and scalable REST API architecture

🎨 React Frontend — Interactive UI styled with TailwindCSS


🛠️ Prerequisites

Ensure the following are installed on your system:

Tool	Required Version	Description
Python
	3.10+	Backend runtime
pip / uv
	latest	Dependency manager
Node.js
	≥ 18	For running React frontend
MongoDB
	latest	Database (local or Atlas)
Git
	—	Version control


📁 Project Structure
food-delivery-system/
├── frontend/       # React + Tailwind app
├── backend/        # FastAPI + LangChain + MongoDB + FAISS
├── docs/        # Documentation
└── README.md

🎨 Frontend Setup
cd frontend
npm install
npm run dev


Runs the development server at http://localhost:5173/
 (default for Vite).

⚙️ Backend Setup
cd backend
python -m venv venv
# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

🔐 Environment Variables

Create a .env file in the backend directory with:

MONGO_URI=your_mongodb_uri
OPENAI_API_KEY=your_openai_key
JWT_SECRET=your_secret_key

▶️ Run the Backend
uvicorn app.main:app --reload


Runs the API server at http://localhost:8000
.

🧩 Tech Stack Overview
Layer	Technology	Description
Frontend	React, CSS, Vite	Modern UI framework
Backend	FastAPI, LangChain, Langgraph & APIs
Database	MongoDB	NoSQL document storage
Vector Search	FAISS	Semantic retrieval for menu data
Language Model	OpenAI (or local model)	Query understanding & reasoning
🧠 Core Modules (Backend)
<!-- Module	Purpose
semantic_retrieve	Retrieves dishes using vector embeddings
intent_extraction	Extracts intents (e.g., “price < 20”, “vegan”)
metadata_filter	Applies structured constraints
validation	Ensures relevant dish matching
orchestrator	Coordinates multi-step reasoning -->
🧪 Running Tests
pytest


or run module-wise:

pytest tests/test_semantic_retrieve.py

🧰 Development Notes

Use modularized service, model, and router layers for maintainability.

<!-- Ensure all routes are prefixed under /api/v1. -->

Follow consistent naming (snake_case for backend, camelCase for frontend).

Keep embeddings and FAISS index files under backend/app/vector_store/.

🤝 Contributing

Contributions are welcome!
Create a feature branch and submit a pull request:

git checkout -b feature/your-feature
git push origin feature/your-feature

📜 License

This project is licensed under the MIT License.