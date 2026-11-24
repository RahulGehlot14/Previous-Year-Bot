# Previous Year Question Paper Analyzer (PYQ Analyzer)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-3F4F75.svg)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An AI-powered academic analytics dashboard that enables university students and educators to upload multiple previous-year examination papers, automatically extract and classify questions into syllabus topics using OpenAI LLMs or a deterministic rule-based engine, compute empirical recurrence frequencies, identify high-yield preparation priorities, and generate publication-ready visual reports.

---

## 🌟 Key Features

1. **Multi-Format Document Ingestion**
   - Drag-and-drop batch upload for **PDF**, **DOCX**, and **TXT** files.
   - Text extraction powered by **PyMuPDF (`fitz`)** and **python-docx**.
   - Scanned PDF detection with graceful **Tesseract-OCR** fallback.
   - Robust document cleaning: strips repeated headers, footers, roll numbers, and exam timestamps while preserving question numbering and mathematical formulas.
   - Content hashing (**SHA-256**) to avoid storing and counting duplicate papers.

2. **Smart Question Extraction Engine**
   - Automatically identifies and separates numbered questions (`Q1`, `1.`, `Question 1`, Roman numerals `I.`, `II.`).
   - Recursively detects and parses subquestions (`a)`, `b)`, `(i)`, `(ii)`).
   - Identifies marks allocations (e.g. `[10 Marks]`, `(5)`, `[CO1, 7M]`).

3. **Hybrid AI & Rule-Based Topic Classification**
   - **OpenAI LLM Integration**: Generates structured JSON matching standard curriculum taxonomies.
   - **Deterministic Fallback (Demo Mode)**: Works out-of-the-box offline without an external API key using rich domain taxonomies.
   - Multi-year topic normalization ensures questions like *"Define 1NF, 2NF and 3NF"* (2022) and *"Explain database normalization and anomalies"* (2024) are mapped to the exact same topic (`Database Normalization`).
   - Identifies Bloom's Taxonomy Level (*Remember, Understand, Apply, Analyze, Evaluate, Create*), Question Type (*Theory, Numerical, Code/Design, Derivation*), and Difficulty (*Easy, Medium, Hard*).

4. **Topic Frequency Analytics (Pandas)**
   - Computes total question occurrences per topic, distinct academic years appeared, distinct paper count, and curriculum percentage share.
   - Distinguishes between question occurrences and paper counts to avoid double-counting.
   - Cross-year topic distribution matrices and unit-wise breakdowns.

5. **Historical Priority Scoring Formula**
   - Transparent, empirical priority formula:
     $$\text{Priority Score} = \left(\frac{\text{Topic Frequency}}{\text{Max Topic Frequency}} \times 60\right) + \left(\frac{\text{Years Appeared}}{\text{Total Years}} \times 40\right)$$
   - Categorizes topics into **Very High Priority** ($\ge 75$), **High Priority** ($\ge 50$), **Medium Priority** ($\ge 25$), and **Low Priority** ($< 25$).
   - Provides concrete study strategies and links representative past exam questions.
   - Clear historical disclaimer stating that scores reflect historical exam trends, not guaranteed predictions.

6. **Interactive Visualizations (Plotly)**
   - Horizontal bar chart of Top 10 frequently asked topics.
   - Topic distribution donut chart.
   - Year-wise line chart tracking question volume across exam cycles.
   - Grouped bar chart comparing topics across academic years.
   - Topics vs. Academic Years heatmaps.
   - Syllabus unit-wise stacked bar charts.

7. **Searchable Question Bank & Manual Calibration**
   - Keyword search across questions, topics, subtopics, and metadata.
   - Multi-parameter filtering by Subject, Year, Unit, Topic, Difficulty, and Bloom Level.
   - Inline question and classification editing with instant SQLite database synchronization.

8. **Multi-Format Report Exports**
   - **PDF Report**: Publication-quality report generated with **ReportLab** containing metadata, KPIs, topic frequency tables, priority recommendations, and legal disclaimers.
   - **Excel Report (.xlsx)**: 5 formatted worksheets (*Summary, Topic Frequency, Priority Recommendations, Year Distribution, Question Bank*).
   - **CSV**: Separate exports for Questions dataset and Topic frequencies.
   - **JSON**: Complete structured question classification schema.

---

## 🏗️ Architecture & Technology Stack

```
Previous Year Question Paper Analyzer
│
├── Frontend: Streamlit, Plotly, Custom HTML/CSS
├── Backend: Python 3.11+, Pandas, NumPy
├── AI / NLP: OpenAI API (Structured JSON) + Rule-Based Taxonomy Engine
├── Document Processing: PyMuPDF (fitz), python-docx, pytesseract, Pillow
├── Storage: SQLite3 (Foreign keys, Indexes, Cascade deletes)
└── Reporting: ReportLab (PDF), openpyxl (Excel)
```

### Folder Structure

```
├── app.py                       # Main Streamlit application orchestrator
├── config.py                    # Global paths, weights, and LLM configuration
├── requirements.txt             # Python dependencies
├── .env.example                 # Example environment variables template
├── .gitignore                   # Git ignore rules
├── README.md                    # Detailed documentation
│
├── database/
│   ├── db_manager.py            # SQLite thread-safe CRUD & KPI manager
│   └── schema.sql               # Database schema definition
│
├── modules/
│   ├── document_processor.py    # PDF/DOCX/TXT text extraction & OCR
│   ├── question_extractor.py    # Pattern matching & marks extraction
│   ├── ai_classifier.py         # OpenAI LLM & Rule-based fallback classifier
│   ├── topic_analyzer.py        # Pandas aggregation & distribution matrices
│   ├── visualization.py         # Interactive Plotly chart builders
│   ├── report_generator.py      # PDF, Excel, CSV, and JSON report generator
│   └── priority_predictor.py    # Priority formula scoring & category mapping
│
├── pages/
│   ├── dashboard.py             # KPI overview & top trends
│   ├── upload.py                # Drag-and-drop paper ingestion
│   ├── question_analysis.py     # Detailed question cards & editor
│   ├── topic_frequency.py       # Full frequency rankings & unit breakdown
│   ├── year_analysis.py         # Multi-year heatmaps & trajectory charts
│   ├── important_topics.py      # Priority tiers & past exam questions
│   ├── question_bank.py         # Searchable question repository
│   ├── export_reports.py        # Report downloads (PDF, Excel, CSV, JSON)
│   └── settings.py              # LLM configuration & database management
│
├── utils/
│   ├── helpers.py               # SHA-256 hashing, formatting, text cleaning
│   ├── validators.py            # Upload & year validation routines
│   └── styling.py               # Custom CSS injection, KPI cards, badges
│
├── assets/
│   └── custom.css               # Modern UI styling & typography
│
├── sample_data/
│   ├── DBMS_PYQ_2022.txt        # Synthetic DBMS exam paper (2022)
│   ├── DBMS_PYQ_2023.txt        # Synthetic DBMS exam paper (2023)
│   ├── DBMS_PYQ_2024.txt        # Synthetic DBMS exam paper (2024)
│   └── seed_data.py             # Automatic sample database seeder
│
├── uploads/                     # Upload staging directory
├── exports/                     # Generated export files
│
└── tests/
    ├── test_extraction.py       # Extraction & document processor tests
    ├── test_analyzer.py         # Pandas aggregation & priority scoring tests
    └── test_classifier.py       # Topic classifier & taxonomy tests
```

---

## 🚀 Installation & Quick Start

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12 installed on your machine.
- *(Optional)* Tesseract-OCR binary installed if you plan to extract text from scanned, image-only PDFs.

### 2. Clone or Open Workspace
```bash
cd "c:\Users\Dell\Downloads\Previous Year Bot"
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure OpenAI API Key
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```
> **Note:** An API key is **optional**. If omitted, the application operates in **Rule-Based Demo Mode** with high-accuracy domain taxonomies for instant demonstrations.

### 5. Launch the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Testing with Pre-loaded Sample Data

To verify all features immediately without uploading your own papers:
1. Open the application.
2. In the Dashboard or in **Settings**, click **"🚀 Load Sample DBMS Dataset (2022-2024)"**.
3. The system will index 3 academic years of synthetic DBMS question papers, extract and classify 30 questions, compute frequency distributions, and populate the dashboard and charts instantly.

---

## ⚙️ Running Automated Tests

Run the full pytest suite:
```bash
pytest -v
```

This verifies:
- `test_extraction.py`: Question splitting, subquestion handling, marks detection, and empty document safeguards.
- `test_analyzer.py`: Pandas frequency counts, unique year appearances, and the priority scoring formula.
- `test_classifier.py`: Rule-based taxonomy mapping, multi-year topic consistency, Bloom's level inference, and JSON parsing.

---

## 🛡️ Security & Privacy
- **No Hardcoded Credentials**: API keys are retrieved from environment variables or active session state.
- **SQL Injection Prevention**: All SQLite queries use parameterized placeholders (`?`).
- **File Validation**: File extensions, sizes, and content types are strictly validated before processing.
- **Content Execution Safety**: Uploaded files are parsed purely as text and never executed as code.

---

## 📜 Disclaimer
The priority rankings, topic frequencies, and study recommendations generated by PYQ Analyzer are derived strictly from empirical historical examination trends. They are designed to help students optimize their revision schedule and do not constitute an official guarantee or prediction of future examination questions.

---

## 📄 License
This project is licensed under the MIT License.
