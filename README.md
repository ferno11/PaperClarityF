# GenAI Legal Tool

## 📘 Objective
Turn complex legal documents into **plain-English summaries + risk alerts**, empowering users to make informed decisions.

## 🚀 Features
- **PDF Text Extraction**: Extract text from both regular and scanned PDFs using OCR
- **Advanced Document Processing**: Clean and preprocess legal documents with enhanced boilerplate detection and intelligent structure preservation
- **Clause Splitting**: Automatically split legal documents into individual clauses with intelligent categorization
- **Smart Categorization**: Auto-tag clauses by type (Payment, Termination, Liability, Property, etc.)
- **Multi-format Support**: Handle various legal document types (rental agreements, loan documents, NDAs, etc.)
- **OCR Capability**: Process scanned documents using Tesseract OCR with OCR error correction
- **Comprehensive Dataset**: 27+ legal document samples for training and testing
- **Clause Analysis**: Generate detailed summaries and statistics of extracted clauses
- **AI-Powered Clause Summarization**: Generate plain-English summaries, key points, and risk assessments for each clause using Google's Gemini API
- **Enhanced Validation System**: Automatic quality checks for summaries including completeness, consistency, and accuracy
- **Advanced Confidence Scoring**: Multi-factor confidence metrics based on text complexity, entity preservation, and content characteristics
- **Priority-Based Risk Assessment**: Enhanced risk evaluation using a weighted scoring system to identify the highest risk factors
- **Fast Processing Mode**: CLI flag (--fast) to skip delays for testing with large datasets
- **Structured Output Schema**: Separated metadata from AI output for better frontend integration
- **Comprehensive Metrics**: Detailed accuracy and consistency metrics for batch processing

### Example Clause Summary

**Original Clause (Late Payment):**
```
In the event that Tenant fails to pay rent when due, Tenant shall pay a late fee of 5% of the monthly rent. If rent remains unpaid for more than 15 days, Landlord may initiate eviction proceedings without further notice.
```

**AI-Generated Summary:**
```json
{
  "summary": "This clause establishes penalties for late rent payment, including a 5% late fee and potential eviction without notice after 15 days of non-payment.",
  "risk": "High",
  "reason": "The clause imposes significant financial penalties and allows for eviction without additional notice, which could result in housing loss with minimal warning."
}
```

Our system uses a hybrid approach combining AI analysis with keyword-based risk assessment to provide accurate and consistent results.

## 🛠 Tech Stack
- **Frontend:** Streamlit (ready for development)
- **Backend:** FastAPI + Uvicorn (ready for development)
- **AI:** OpenAI API (integrated), Google Gemini API (integrated), FAISS for vector search
- **PDF Processing:** PyMuPDF, pdfplumber, pypdfium2, pdfminer.six
- **OCR:** Tesseract OCR + pytesseract
- **Document Processing:** python-docx, Pillow, lxml
- **Data Processing:** pandas, numpy, pyarrow
- **Web Framework:** tornado, httpx, requests
- **Utilities:** tqdm, click, colorama, watchdog

## 📊 Current Dataset
The project includes a comprehensive collection of legal documents:

### Document Types (27 files total):
- **Rental Agreements** (9 documents)
- **Loan Agreements** (5 documents)
- **Terms of Service** (5 documents)
- **NDAs** (2 documents)
- **Employment Agreements** (2 documents)
- **Vendor Agreements** (2 documents)
- **Insurance Documents** (2 documents)
- **Consent Forms** (1 document)

## 🏗 Project Structure
```
genai-legal-tool/
├─ frontend/           # Streamlit UI (ready for development)
├─ backend/            # FastAPI backend
│  ├─ main.py             # FastAPI application and endpoints
│  ├─ qa.py               # Question answering functionality
│  └─ utils.py            # Utility functions for backend
├─ ai_models/          # AI integration scripts
│  └─ summarize_clauses.py # Clause summarization with Gemini API
├─ utils/              # Document processing utilities
│  ├─ dynamic_clause_splitter.py  # Advanced clause splitting
│  └─ dynamic_pdf_extractor.py    # PDF text extraction with OCR
├─ docs/               # Document collection
│  ├─ processed/       # Extracted text files (27 files)
│  └─ clauses/         # Individual clause files (74+ files)
├─ run.py              # Entry point script to run the FastAPI server
├─ requirements.txt    # Python dependencies
└─ README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Tesseract OCR (for scanned PDF processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Endless-Mrianl/genai_legal.git
   cd genai-legal-tool
   ```

2. **Create virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR** (for scanned PDF processing)
   - Windows: Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
   - Install with "Add to PATH" option
   - Default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`

### Running the Application

1. **Start the FastAPI backend**
   ```bash
   python run.py
   ```
   The API will be available at http://127.0.0.1:8000
   
   API Documentation is available at:
   - http://127.0.0.1:8000/docs (Swagger UI)
   - http://127.0.0.1:8000/redoc (ReDoc)
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR (Windows)**
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install with "Add to PATH" option
   - Default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`

### Usage

1. **Extract text from PDFs**
   ```bash
   python utils/extract_text.py
   ```
   This will process all PDFs in `docs/` and save clean text files to `docs/processed/`

2. **Split documents into clauses**
   ```bash
   python utils/split_clauses.py
   ```
   Basic clause splitting with automatic categorization

3. **Advanced clause processing**
   ```bash
   python utils/split_clauses_v2.py
   ```
   Enhanced clause splitting with improved categorization

4. **Generate clause analysis report**
   ```bash
   python utils/clause_summary_v2.py
   ```
   Create detailed analysis and statistics of extracted clauses

5. **Test Tesseract installation**
   ```bash
   python utils/test_tesseract.py
   ```

6. **Validate text cleaning**
   ```bash
   python utils/test_cleaning.py
   ```

## 📋 Current Status

### ✅ Completed
- [x] Virtual environment setup
- [x] Library installation (97 dependencies installed)
- [x] Legal document dataset collection (27 PDFs)
- [x] PDF text extraction system with OCR
- [x] Text cleaning and preprocessing pipeline
- [x] Basic clause splitting functionality
- [x] Advanced clause splitting with smart categorization
- [x] Clause analysis and reporting system
- [x] Comprehensive document processing pipeline
- [x] Test suite for validation and debugging
- [x] AI-powered clause summarization with Gemini API

### 🚧 In Progress
- [ ] Streamlit frontend development
- [ ] FastAPI backend implementation
- [ ] AI model integration for summarization
- [ ] Risk assessment algorithms
- [ ] Document comparison tools

### 📝 Planned Features
- [ ] Document upload interface
- [ ] AI-powered document summarization
- [ ] Risk analysis and alerts
- [ ] Document comparison tools
- [ ] Legal clause extraction
- [ ] Contract analysis dashboard

## 🔧 Technical Details

### Document Processing Pipeline
1. **PDF Text Extraction**: 
   - Primary: `pdfplumber` for text-based PDFs
   - OCR Fallback: `pytesseract` + `PyMuPDF` for scanned documents
2. **Text Cleaning**: Removes headers, footers, page numbers, and extra whitespace
3. **Clause Splitting**: 
   - Intelligent detection of clause boundaries
   - Automatic categorization (Payment, Termination, Liability, etc.)
   - Smart naming and tagging system
4. **Analysis & Reporting**: 
   - Generate detailed statistics and summaries
   - Category breakdown and clause distribution
   - File size and content analysis
5. **Output**: Clean UTF-8 text files and individual clause files ready for AI processing

### Clause Processing Features
- **Smart Categorization**: Automatically tags clauses by type:
  - Payment, Termination, Liability, Property, Duration
  - Obligations, Rights, Restrictions, Default, Remedies
- **Intelligent Splitting**: Detects clause boundaries using:
  - Numbered patterns (1., 2), 3-, 4:)
  - Section headings (UPPERCASE words)
  - Legal markers (WHEREAS, THEREFORE, etc.)
  - Paragraph breaks as fallback
- **File Organization**: Creates individual clause files with descriptive names
- **Analysis Reports**: Generates comprehensive statistics and summaries

### Supported Document Formats
- PDF (text-based and scanned)
- Automatic OCR detection for image-based PDFs
- UTF-8 text output for international character support

## 👥 Team Members
- [Add your names here]

## 📄 License
[Add license information]

## 🤝 Contributing
[Add contribution guidelines]

## 📞 Support
[Add support/contact information]