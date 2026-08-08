# ⚖️ Legal Sathi AI

Legal Sathi AI is an AI-powered legal document assistant that helps users understand complex legal documents in simple and easy-to-understand language.

Users can upload PDF or image documents, and the application extracts the text, analyzes it using AI, simplifies complex legal terminology, and provides explanations in multiple languages.

---

## 🌐 Live Demo

https://YOUR-FRONTEND-URL.vercel.app
---

## ✨ Features

- 📄 Upload legal documents in PDF or Image format
- 👁️ Vision AI-powered text extraction for images and scanned PDFs
- 📑 Text extraction from digital PDFs using PyMuPDF
- 🤖 AI-powered legal document analysis
- 📝 Simplifies complex legal terminology into plain English
- 🌍 AI-powered translation support (English, Malayalam & Hindi)
- ⚡ Fast document processing
- 🔒 Secure document handling

---

## 🛠️ Tech Stack

### Frontend

- React.js
- Vite
- Tailwind CSS
- React Router
- Axios
- React Markdown

### Backend

- Django
- Django REST Framework
- Groq API (LLaMA)
- PyMuPDF
- Pillow
- Python-dotenv

---

## 📂 Project Structure

```
LegalSathi-v2/
│
├── backend/
│   ├── core/
│   ├── documents/
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

## 🚀 How It Works

1. Upload a legal document (PDF or Image).
2. 
The application extracts the document text:

- Digital PDFs → using **PyMuPDF**
- Images & Scanned PDFs → using a **Vision AI Model**
  
3.The extracted content is analyzed using an AI-powered Large Language Model (LLM).
4. Complex legal terminology is converted into simple English.
5. Users can optionally translate the simplified analysis into Malayalam or Hindi.

---

## 🌍 Translation Support

The AI first generates a simplified English explanation of the legal document.

Users can then choose their preferred language:

- 🇬🇧 English
- 🇮🇳 Hindi
- 🇮🇳 Malayalam

Translations are generated on demand using AI and are usually available within a few seconds.

---

## 📸 Screenshots

Add screenshots of:

- Home Page
- Upload Page
- AI Analysis
- Translation Feature

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/A-adilajaleel/LegalSathi-V2.git
```

### Backend

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## 🔑 Environment Variables

Create a `.env` file inside the backend directory.

```
GROQ_API_KEY=your_groq_api_key
```

---

## Future Improvements


- 🔍 Legal Risk Detection
- 📄 Download AI-Generated Reports
- 👤 User Authentication & Dashboard
- 📂 Document History

---

## 👩‍💻 Author

**Adila Jaleel**

GitHub:
https://github.com/A-adilajaleel

---

## 📄 License

This project is created for educational and portfolio purposes.
