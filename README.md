# ZUS Coffee Internal Assistant

A full-stack RAG (Retrieval-Augmented Generation) application designed to help ZUS Coffee employees instantly access internal information about products, outlets, food, and drinks through natural language queries.

**🔄 Adaptable to Any Retail Business**: This solution is not limited to coffee shops. The same architecture can be deployed for any retail business—restaurants, fashion stores, electronics retailers, or service providers. Simply provide your internal data (products, locations, services, pricing), and the system adapts to your specific business needs without code changes.

## 🔗 Links

- **🎥 Video Demo**: [Watch on YouTube](https://youtu.be/COY4JfGfMv8)
- **🌐 Live Demo**: [https://shortcut-asia-internship-project.vercel.app/](https://shortcut-asia-internship-project.vercel.app/)

## 🎯 Problem Statement

ZUS Coffee staff often need quick access to information about:

- Product details (drinkware, merchandise)
- Outlet locations and addresses
- Food and drink menu items
- Product pricing and availability

Searching through spreadsheets, PDFs, or multiple systems is time-consuming and inefficient. This assistant provides instant, accurate answers through a conversational AI interface.

**Universal Application**: This same problem exists across all retail sectors—from grocery stores needing product locations, to car dealerships tracking inventory, to hotel chains managing amenities. Any business with internal data can benefit from this AI-powered knowledge base.

## ✨ Key Features

### 1. **AI-Powered Chatbot (RAG System)**

- **Natural Language Queries**: Ask questions in plain English like "What outlets are in Kuala Lumpur?" or "What's the price of the CEO Latte?"
- **Intelligent Retrieval**: Uses FAISS vector search to find relevant information from the knowledge base
- **Context-Aware Responses**: Powered by Google Gemini LLM with LangChain agents for accurate, contextual answers
- **Real-Time Streaming**: Responses stream in real-time with proper Markdown formatting

### 2. **Admin Dashboard (CRUD Operations)**

- **Data Management**: Full Create, Read, Update, Delete operations for all data types
- **Four Data Categories**:
  - Outlets (stores and locations)
  - Products (drinkware and merchandise)
  - Food (menu items)
  - Drinks (beverage menu)
- **Protected Routes**: Secure authentication for admin access
- **Instant Updates**: Changes immediately reflect in the AI chatbot's knowledge base

## 🏗️ Architecture

### **Frontend** (Next.js 15)

```
├── Next.js 15 (App Router)
├── TypeScript
├── Tailwind CSS
├── React Context (Authentication)
└── Axios (API Client)
```

**Key Pages:**

- `/` - Main chat interface
- `/admin` - Protected admin dashboard with CRUD operations

### **Backend** (FastAPI)

```
├── FastAPI (Python 3.11)
├── SQLite (Data Storage)
├── FAISS (Vector Search)
├── LangChain (AI Agent Framework)
├── Google Gemini (LLM)
└── Sentence Transformers (Embeddings)
```

**API Endpoints:**

- `/chat` - AI chatbot endpoints
- `/products`, `/outlets`, `/food`, `/drinks` - CRUD operations
- `/embeddings` - Vector search management
- `/admin` - Authentication

### **Data Flow**

```
┌─────────────────┐
│  User Question  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  LangChain Agent        │
│  (Google Gemini)        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  RAG Tool               │
│  - Embeds query         │
│  - Searches FAISS index │
│  - Retrieves from SQLite│
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Contextual Response    │
│  (Streamed to User)     │
└─────────────────────────┘
```

## 🚀 Tech Stack

| Layer          | Technology                                        |
| -------------- | ------------------------------------------------- |
| **Frontend**   | Next.js 15, TypeScript, Tailwind CSS              |
| **Backend**    | FastAPI, Python 3.11                              |
| **Database**   | SQLite                                            |
| **Vector DB**  | FAISS (Facebook AI Similarity Search)             |
| **AI/ML**      | LangChain, Google Gemini, Sentence Transformers   |
| **Deployment** | Docker, Vercel (Frontend), Google Cloud (Backend) |

## 📦 Project Structure

```
shortcut-asia-internship-project/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # RAG and SQL services
│   │   └── agent/               # LangChain agent & tools
│   ├── data/                    # JSON data files
│   ├── database/                # SQLite database
│   ├── index/                   # FAISS embeddings
│   ├── scraper/                 # Web scrapers
│   ├── ingestion/               # Data ingestion scripts
│   └── Dockerfile
│
└── frontend/
    ├── app/
    │   ├── page.tsx             # Chat interface
    │   └── admin/page.tsx       # Admin dashboard
    ├── components/              # React components
    ├── contexts/                # Auth context
    ├── lib/api.ts              # API client
    └── types/                   # TypeScript types
```

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Set environment variable
export GOOGLE_API_KEY=your_gemini_api_key

# Run data ingestion
python ingestion/ingest_scraped_data_to_sqlite.py
python ingestion/ingest_data_into_faiss_embeddings.py

# Start server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start dev server
npm run dev
```

## 🐳 Docker Deployment

```bash
# Backend
cd backend
docker build -t zus-backend .
docker run -p 8000:8000 -e GOOGLE_API_KEY=your_key zus-backend

# Frontend
cd frontend
docker build -t zus-frontend .
docker run -p 3000:3000 zus-frontend
```

## 🔑 Environment Variables

**Backend:**

- `GOOGLE_API_KEY` - Google Gemini API key (required)
- `ADMIN_PASSWORD` - Admin dashboard password (default: admin123)
- `PORT` - Server port (default: 8000)

**Frontend:**

- `NEXT_PUBLIC_API_URL` - Backend API URL

## 🌐 Scalability & Business Adaptability

### How to Adapt This System for Any Retail Business

This platform is designed to be **business-agnostic**. Here's how to customize it:

1. **Data Ingestion**: Replace the ZUS Coffee data with your business data:

   - Update the web scrapers or provide CSV/JSON files
   - Modify the SQLite schema to match your data structure (e.g., "Products" → "Services", "Outlets" → "Branches")

2. **Admin Dashboard**: The CRUD interface automatically adapts:

   - Change tab labels and field names
   - Add/remove data categories as needed
   - Update validation rules for your specific requirements

3. **AI Knowledge Base**: The RAG system works with any text data:

   - Product catalogs → Service descriptions
   - Store locations → Delivery zones
   - Menu items → Appointment types
   - Pricing → Package deals

4. **Example Use Cases**:
   - **Fashion Retail**: "What's the stock status of size M blue jeans?"
   - **Electronics Store**: "Which outlets have the iPhone 15 in stock?"
   - **Restaurant Chain**: "What are today's special promotions?"
   - **Real Estate**: "Show me 3-bedroom properties under $500k in downtown"

**Key Advantage**: Once deployed, non-technical staff can update the knowledge base through the admin dashboard—no developer intervention required.
