📄 AI-Powered Research Paper Summarizer

An end-to-end NLP web application that automatically summarizes research papers (PDF format) using state-of-the-art Transformer models.

This project extracts text from uploaded research papers and generates concise summaries using Facebook’s BART large CNN model.

🚀 Features

📄 Upload research paper (PDF)
🧹 Automatic text extraction and cleaning
✂️ Smart text chunking for large documents
🤖 Abstractive summarization using facebook/bart-large-cnn
🎨 Clean Streamlit UI with pastel theme
⚡ Lazy model loading for performance optimization

🏗️ Project Architecture
User Upload (PDF)
        ↓
Streamlit Frontend (app.py)
        ↓
Backend Processing (summarizer.py)
        ↓
Text Extraction → Cleaning → Chunking
        ↓
BART Transformer Model
        ↓
Generated Summary


 🛠️ Tech Stack

Python
Streamlit
HuggingFace Transformers
Facebook BART (bart-large-cnn)
PyTorch
pdfplumber


