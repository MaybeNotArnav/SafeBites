# 🍴 Food Delivery System – Local Development Setup

This repo contains both **frontend** (React + Tailwind) and **backend** (FastAPI + LangChain + MongoDB).  
Follow the steps below to run locally.  

---

## 🛠 Prerequisites

Make sure you have the following installed:

- **Python** 3.10+ → [Download](https://www.python.org/downloads/)  
- **pip** or **uv** (for dependency management)  
- **Node.js** (>=18) + npm (for frontend only) → [Download](https://nodejs.org/en/)  
- **MongoDB** (local or Atlas cloud) → [Docs](https://www.mongodb.com/docs/manual/installation/)  
<!-- - **Redis** (for Celery background tasks, optional at this stage)   -->
- **Git**  

---

## 📂 Project Structure
/frontend → React  app
/backend → FastAPI app with LangChain, MongoDB, FAISS


---

## 🎨 Frontend Setup
   cd frontend
   npm install
   npm run dev

## Backend Setup
    cd backend
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    Create .env file for storing private variables such as database urls, openAI api keys, jwt_secret.
    uvicorn app.main:app --reload

## Dish CRUD APIs implemented:
   1. POST   /dishes/               → Create a new dish
   2. GET    /dishes/{dish_id}      → Get dish by ID
   3. GET    /dishes/               → Get all dishes
   4. PUT    /dishes/{dish_id}      → Update a dish
   5. DELETE /dishes/{dish_id}      → Delete a dish

## User CRUD APIs implemented:
   1. POST   /users/signup          → Create new user
   2. POST   /users/login           → Login & get token
   3. GET    /users/me              → Get logged-in user profile
   4. PUT    /users/me              → Update profile
   5. DELETE /users/me              → Delete user
   6. GET    /users/{id}            → Get user by ID