# 🤝 Contributing Guidelines

Thank you for considering contributing to the **SafeBites** project!  
We appreciate your time and effort in helping us improve and grow this AI-powered food delivery platform.  

Please read the following guidelines carefully before contributing.

---

## 🧭 Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Setting Up the Environment](#setting-up-the-environment)
4. [Branching & Workflow](#branching--workflow)
5. [Commit Message Convention](#commit-message-convention)
6. [Pull Request Guidelines](#pull-request-guidelines)
7. [Code Style & Best Practices](#code-style--best-practices)
8. [Testing](#testing)
9. [Reporting Issues](#reporting-issues)

---

## 🏁 Getting Started

Before contributing, make sure you have:
- Read the [README.md](../README.md)
- Installed all prerequisites (Python, Node.js, MongoDB)
- Set up `.env` files using `.env.example`
- Tested your local setup for both backend and frontend

Once everything runs locally, you’re ready to contribute 🚀

---

## 📂 Project Structure

food-delivery-system/
├── backend/ # FastAPI + LangChain + MongoDB
│ ├── app/
│ ├── tests/
│ └── requirements.txt
├── frontend/ # React + Tailwind app
│ ├── src/
│ └── package.json
└── docs/ # Documentation (this folder)

yaml

---

## ⚙️ Setting Up the Environment

Follow the setup steps in the [README.md](../README.md) for detailed backend and frontend setup.  
Ensure both are running before creating new features.

---

## 🌿 Branching & Workflow

We follow the **feature-branch workflow**:

```bash
git checkout -b feature/<your-feature-name>
Branch Naming Convention
Type	Example	Description
feature/	feature/add-recommendation-module	For new features
fix/	fix/mongodb-connection-error	For bug fixes
refactor/	refactor/vector-service	For improving existing code
docs/	docs/update-readme	For documentation updates

Typical Flow
bash
Copy code
# Create branch
git checkout -b feature/add-user-api

# Commit changes
git add .
git commit -m "feat: add new user creation API"

# Push branch
git push origin feature/add-user-api
📝 Commit Message Convention
We follow the Conventional Commits format:

cpp
Copy code
<type>(optional scope): <short summary>
Type	Meaning
feat	New feature
fix	Bug fix
docs	Documentation update
style	Code style changes (no logic)
refactor	Code restructuring
test	Adding or updating tests
chore	Maintenance tasks

Examples:

feat(api): add metadata filtering endpoint

fix(db): resolve MongoDB schema mismatch

refactor(vector): optimize FAISS index lookup

🔄 Pull Request Guidelines
Make sure all your commits follow the convention above.

Ensure code builds and passes tests before submitting.

Keep PRs focused — one feature or fix per PR.

Include a brief description of what your PR does.

Link any related issues or discussions.

PR Title Example:

scss
Copy code
feat(frontend): implement restaurant search component
💅 Code Style & Best Practices
Python (Backend)
Follow PEP8 style guide.

Use descriptive variable names.

Add docstrings for functions and services.

Keep modules modular — separate routes, models, and services.

JavaScript/React (Frontend)
Use functional components.

Follow ESLint + Prettier formatting.

Keep components small and reusable.

Use consistent naming: camelCase for variables, PascalCase for components.

🧪 Testing
Run all backend tests before submitting a PR:

bash
Copy code
cd backend
pytest
For frontend testing (if added):

bash
Copy code
cd frontend
npm test
✅ All tests must pass before your PR is merged.

🐛 Reporting Issues
Found a bug or have a feature request?
Create a detailed issue using the format below:

Issue Template

shell
Copy code
### Description
Briefly describe the problem.

### Steps to Reproduce
1. ...
2. ...

### Expected Behavior
What should happen?

### Environment
OS, Python version, Node version, etc.
❤️ Thank You!
Your contributions make this project better for everyone.
We appreciate every PR, issue, and idea shared 🙌

— The SafeBites Dev Team

yaml
Copy code

---