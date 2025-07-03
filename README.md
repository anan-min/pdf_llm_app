# PDF to LLM Project with Ollama

A Python 3.11 project that converts PDF files to text and sends them to Ollama local LLMs for processing.

## Features

- Extract text from PDF files
- Clean and preprocess text
- Send text to Ollama local LLMs
- Streamlit web interface
- Support for multiple PDF processing libraries

## Prerequisites

- Python 3.11
- pip (Python package installer)
- **Ollama installed and running locally**

## Ollama Setup

### 1. Install Ollama

Visit [ollama.ai](https://ollama.ai) and install Ollama for your operating system.

### 2. Pull a Model

```bash
# Pull a recommended model (choose one)
ollama pull qwen2.5:7b
ollama pull llama3.1:8b
ollama pull mistral:7b
ollama pull qwen2.5:32b  # If you have enough RAM/VRAM
```

### 3. Start Ollama Service

```bash
# Start Ollama server (runs on localhost:11434)
ollama serve
```

### 4. Test Ollama

```bash
# Test with a simple query
ollama run qwen2.5:7b "Hello, how are you?"
```

## Installation

### 1. Clone the Project

```bash
git clone <your-repository-url>
cd pdf-to-llm-project
```

### 2. Create Virtual Environment

```bash
# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### 4. Alternative Manual Installation

If you don't have requirements.txt:

```bash
# Core dependencies
pip install streamlit

# PDF processing libraries
pip install PyPDF2 pdfplumber pymupdf

# Text processing
pip install python-docx

# Ollama integration
pip install requests

# Additional utilities
pip install pandas numpy matplotlib python-dotenv
```


## Usage

### 1. Start the Application

```bash
streamlit run app.py
```

### 2. Access the Web Interface

Open your browser and go to:
```
http://localhost:8501
```
### 


Supported PDF Types
✅ Works with:

Text-based PDFs (created from Word, Google Docs, etc.)
PDFs with embedded text layer
Digital documents with selectable text

❌ Does NOT work with:

Scanned documents
Photos of documents saved as PDF
Image-only PDFs
Old documents converted to PDF without OCR

How to Check if Your PDF Will Work

Test selection: Try to select and copy text from your PDF
If you can select text: ✅ This project will work
If you cannot select text: ❌ You need OCR preprocessing


### 
