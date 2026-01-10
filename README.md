# Smart Approval AI 🚀

### **Built with Google Technologies** | Powered by **Gemini AI**

<p align="center">
  <img src="https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white"/>
  <img src="https://img.shields.io/badge/Firebase-Auth_&_Backend-FFCA28?style=for-the-badge&logo=firebase&logoColor=black"/>
  <img src="https://img.shields.io/badge/Google_Cloud-Platform-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white"/>
  <img src="https://img.shields.io/badge/Google_AI_Studio-Integrated-34A853?style=for-the-badge&logo=google&logoColor=white"/>
</p>

---

## 🎯 Overview

Smart Approval AI is an **AI-powered document analysis platform** that leverages **Google's cutting-edge AI technologies** to automate institutional accreditation review for AICTE and NBA regulatory bodies.

### Why Google Technologies?

| Technology | Usage | Benefit |
|------------|-------|---------|
| **Google Gemini 2.5 Flash** | Document Analysis & Extraction | Fastest, most accurate AI model |
| **Firebase Authentication** | User Management | Enterprise-grade security |
| **Google Sign-In (OAuth 2.0)** | Login | Seamless one-click auth |
| **Firebase Admin SDK** | Role Management | Custom claims for RBAC |
| **Google Cloud Vision** | OCR (Optional) | Industry-leading text recognition |
| **Google AI Studio** | Prompt Engineering | AI model optimization |

---

## 🔥 Google Technology Stack

### 🧠 AI & Machine Learning

#### Google Gemini AI (Primary AI Engine)
```python
# Backend Configuration
GEMINI_MODEL = "gemini-2.5-flash"  # Latest multimodal AI
GEMINI_API_KEY = "your-key"
```

- **Semantic Block Classification** - AI understands document context
- **Structured Data Extraction** - Extracts 10+ information blocks
- **Intelligent KPI Calculation** - Automated performance scoring
- **Compliance Analysis** - AI-powered rule checking

#### Google AI Studio Integration
- Fine-tuned prompts for document analysis
- Multimodal processing (text + tables + images)
- Temperature-controlled outputs for consistency

### 🔐 Firebase Services

#### Firebase Authentication
```typescript
// Frontend - Google Sign-In
import { signInWithPopup, GoogleAuthProvider } from 'firebase/auth';
```

- **Google Sign-In** - Primary authentication method
- **Email/Password** - Secondary auth option
- **Custom Claims** - Role-based access (College/Department)

#### Firebase Admin SDK
```python
# Backend - Token Verification
from firebase_admin import credentials, auth
auth.verify_id_token(id_token)
```

- Server-side token verification
- User role management
- Secure API authorization

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│             FRONTEND (Next.js + Firebase Auth)              │
│         🔐 Google Sign-In | Firebase Authentication         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI + Python)                  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              🧠 Google Gemini 2.5 Flash                 │ │
│  │    Semantic Classification | Data Extraction | KPIs    │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              🔥 Firebase Admin SDK                      │ │
│  │       Token Verification | Custom Claims | Roles       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              ☁️ Google Cloud Infrastructure                  │
│    Cloud Storage | Cloud Run | Cloud Functions (Ready)     │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### Core Capabilities
- 📄 **Multi-format Document Upload** - PDF, DOCX, images
- 🧠 **Gemini AI Analysis** - Semantic understanding of documents
- 📊 **KPI Calculation** - FSR, Infrastructure, Placements, etc.
- ✅ **Compliance Checking** - Automated rule verification
- 📈 **Trend Analysis** - Historical performance tracking
- 📝 **PDF Report Generation** - Official accreditation reports
- 💬 **AI Chatbot** - Gemini-powered assistant

### Supported Modes
- **AICTE Mode** - Technical education evaluation
- **NBA Mode** - National Board of Accreditation

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Cloud Account (for Gemini API)
- Firebase Project

### Environment Setup

```bash
# Clone repository
git clone https://github.com/Nishant-aiml/Techsprint-Iveri.git
cd Techsprint-Iveri

# Backend setup
cd backend
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### Configure Google Services

Create `.env` file:

```env
# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash

# Firebase
FIREBASE_PROJECT_ID=accreditation-platform
FIREBASE_SERVICE_ACCOUNT_BASE64=base64-encoded-credentials

# OpenAI (Fallback)
OPENAI_API_KEY=your-openai-key
```

### Run the Application

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

Access at: `http://localhost:3000`

---

## 🏗️ Deployment

### Live URLs
- **Frontend**: https://smartapprovalai.vercel.app
- **Backend**: https://smartapprovalai.up.railway.app

### Production Stack
| Service | Platform | Google Tech Used |
|---------|----------|------------------|
| Frontend | Vercel | Firebase Auth, Google Sign-In |
| Backend | Railway | Gemini AI, Firebase Admin SDK |
| Storage | Cloud Storage | Google Cloud Storage |

---

## 📖 Documentation

- [Google Tech Stack Details](./GOOGLE_TECH_STACK.md)
- [API Documentation](./backend/README.md)
- [Frontend Guide](./frontend/README.md)

---

## 👥 Team

Built for **Techsprint 2026** 🏆

---

## 📜 License

MIT License - See [LICENSE](./LICENSE) for details

---

<p align="center">
  <strong>Built with ❤️ using Google Technologies</strong>
  <br/>
  <img src="https://img.shields.io/badge/Gemini-AI-4285F4?style=flat&logo=google&logoColor=white"/>
  <img src="https://img.shields.io/badge/Firebase-Backend-FFCA28?style=flat&logo=firebase&logoColor=black"/>
  <img src="https://img.shields.io/badge/Google_Cloud-Infra-4285F4?style=flat&logo=google-cloud&logoColor=white"/>
</p>
