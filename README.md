<h1 align="center">🤖 Smart Support System</h1>

<p align="center">
  <b>A modern AI-powered Customer Support Platform built with FastAPI + React</b><br/>
  Seamlessly connects users and admins through an intelligent chatbot interface with an advanced admin dashboard for file management, analytics, and query insights.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Framework-FastAPI-blue?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/AI-RAG_Pipeline-orange?style=for-the-badge"/>
</p>

---

## 🚀 Overview

The **Smart Support System** is a full-stack **AI chatbot** that delivers real-time, context-aware responses by processing uploaded knowledge base files.

It uses a **Retrieval-Augmented Generation (RAG)** pipeline to intelligently retrieve relevant document information before generating a response.  
Admins can easily manage files, analyze user interactions, and monitor unanswered queries through a modern **Admin Dashboard**.

> 🎯 Designed as a **portfolio-ready project** showcasing end-to-end full-stack + AI integration skills.

---

## ✨ Features

| 🧩 Category | 🪄 Features |
|--------------|-------------|
| 💬 **Chatbot** | Smart conversational bot powered by a custom RAG pipeline |
| 👤 **Authentication** | Secure user login & registration using JWT |
| 🧑‍💼 **Admin Dashboard** | Upload, delete, and manage files; view analytics |
| 📂 **File Ingestion** | Automatically process PDFs and text files for chatbot training |
| 📈 **Analytics** | Track total queries, failed questions, and user statistics |
| 🔐 **Role-based Access** | Separate dashboards for users and admins |
| 🌍 **Responsive UI** | Built with React + Tailwind CSS for a seamless experience |
| 🧩 **Modular Codebase** | Cleanly separated backend modules for scalability |
| ☁️ **Future Ready** | Optimized for cloud deployment (Render + Vercel) |

---

## 🧠 Tech Stack

| Layer | Technologies Used |
|--------|--------------------|
| 🖥️ **Frontend** | React.js (Vite), Tailwind CSS, Framer Motion |
| ⚙️ **Backend** | FastAPI (Python), Uvicorn, Pydantic |
| 🧠 **AI Logic** | Custom Retrieval-Augmented Generation (RAG) pipeline |
| 🗄️ **Database** | JSON-based storage (Users, Conversations, Analytics), SQLite (History) |
| 🔒 **Authentication** | JSON Web Tokens (JWT) |
| ☁️ **Deployment** | Render (Backend) + Vercel (Frontend) |

---

## 🗂️ Project Structure

smart-support-system/
│
├── backend/
│ ├── app/
│ │ ├── api/
│ │ │ ├── admin_routes.py
│ │ │ ├── auth_routes.py
│ │ │ ├── chat_routes.py
│ │ │ └── user_routes.py
│ │ ├── core/
│ │ │ └── config.py
│ │ ├── models/
│ │ │ └── user_model.py
│ │ ├── services/
│ │ │ ├── auth_service.py
│ │ │ ├── conversation_service.py
│ │ │ ├── ingest_service.py
│ │ │ ├── analytics_service.py
│ │ │ ├── rag_pipeline.py
│ │ │ └── db_service.py
│ │ ├── utils/
│ │ │ └── security.py
│ │ ├── main.py
│ │ ├── database.py
│ │ └── db.py
│
└── frontend/
├── src/
│ ├── pages/
│ │ ├── Login.jsx
│ │ ├── Register.jsx
│ │ ├── Chat.jsx
│ │ └── Dashboard.jsx
│ ├── context/
│ │ └── AuthContext.jsx
│ └── utils/
│ └── api.js
├── package.json
└── vite.config.js


📊 Admin Dashboard
  🧑‍💼 Admin Capabilities:
    ✅ Upload & delete knowledge files  
    📈 View total users, query counts, and analytics
    🔎 Monitor failed queries and performance metrics  

## 🚧 Future Enhancements

| 🚀 Feature | 📝 Description |
|-------------|----------------|
| 🧠 **Human Escalation** | Route low-confidence chatbot queries to human agents for review and resolution |
| 📈 **Advanced Analytics** | Enable filtering by date, topic, and user activity to gain deeper insights |
| 🌍 **Multi-language Support** | Expand chatbot capabilities for multilingual communication |
| ☁️ **Cloud DB Integration** | Replace JSON-based storage with scalable cloud databases like MongoDB or PostgreSQL |
| 🎤 **Voice Input** | Add speech-to-text support for enhanced accessibility and hands-free usage |


👨‍💻 Author

Vijesh Krishna
📍 Bengaluru, India
💼 Aspiring Full Stack + AI Developer


<p align="center"> Made with ❤️ using <b>FastAPI</b> + <b>React</b> <br/> © 2025 Smart Support System. All rights reserved. </p> ```

