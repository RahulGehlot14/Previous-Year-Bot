# Previous Year Question Paper Analyzer (PYQ Analyzer)

[![GitHub Repository](https://img.shields.io/badge/GitHub-RahulGehlot14%2FPrevious--Year--Bot-blue?logo=github)](https://github.com/RahulGehlot14/Previous-Year-Bot)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36+-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-3F4F75.svg)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests Passing](https://img.shields.io/badge/Tests-16%20Passed-brightgreen.svg)]()

An AI-powered academic analytics platform designed for university students, educators, and curriculum planners. Ingest multiple previous-year examination papers, automatically extract individual questions, classify them into standardized syllabus topics using OpenAI LLMs or high-precision rule-based taxonomies, compute empirical recurrence distributions, identify high-yield preparation priorities, generate balanced mock examination papers, and export publication-ready reports.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture & Technology Stack](#-architecture--technology-stack)
- [Project Directory Structure](#-project-directory-structure)
- [Quick Start & Installation](#-quick-start--installation)
- [Configuration](#-configuration)
- [Application Walkthrough](#-application-walkthrough)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Pushing to GitHub](#-pushing-to-github)
- [Security & Compliance](#-security--compliance)
- [License](#-license)

---

## 💡 Overview

Preparing for university examinations often involves analyzing years of past papers manually to guess what topics examiners prefer. **PYQ Analyzer** automates this end-to-end:
1. Ingests raw papers in **PDF**, **DOCX**, and **TXT** formats.
2. Identifies question boundaries, subquestions, and marks.
3. Maps questions to consistent, multi-year curriculum topics.
4. Calculates recurrence percentages and historical priority scores.
5. Generates personalized revision schedules and realistic practice mock papers.
6. Exports high-resolution PDF reports, multi-sheet Excel workbooks, CSVs, and JSON.

---

## 🌟 Key Features

### 1. Multi-Format Document Ingestion
- Batch upload past examination papers (**PDF**, **DOCX**, **TXT**).
- Digital text extraction powered by **PyMuPDF (`fitz`)** and **python-docx**.
- **Scanned PDF Detection & OCR**: Automatically identifies image-only PDFs and invokes **Tesseract-OCR** (`pytesseract` + `Pillow`).
- **Content Hashing (SHA-256)**: Prevents duplicate uploads and protects frequency analytics from double-counting.

### 2. Smart Question Extraction Engine
- Boundary regex pattern matching (`Q1`, `Q.1`, `Question 1`, `1.`, `2)`, Roman numerals `I.`, `II.`).
- Recursively parses subquestions (`a)`, `b)`, `(a)`, `(i)`, `(ii)`).
- Detects marks annotations (e.g. `[10 Marks]`, `(5)`, `[CO1, 7M]`).
- Strips exam boilerplates (roll number blanks, page headers, timestamps) while preserving mathematical symbols and code.

### 3. Hybrid AI & Deterministic Classification
- **OpenAI LLM Integration**: Generates structured JSON matching standard curriculum taxonomies (`gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo`).
- **Deterministic Offline Fallback (Demo Mode)**: Rich domain taxonomies (DBMS, OS, Computer Networks) ensuring consistent topic naming across years without an API key or internet access.
- Identifies **Bloom's Taxonomy Levels** (*Remember, Understand, Apply, Analyze, Evaluate, Create*), **Question Types** (*Theory, Numerical, Code/Design, Derivation*), and **Difficulty** (*Easy, Medium, Hard*).

### 4. Topic Frequency Analytics (Pandas)
- Computes total questions per topic, distinct academic years appeared, distinct paper count, and curriculum percentage share.
- Generates cross-year topic distribution matrices and unit-wise breakdowns.
- Distinguishes question occurrences from paper counts to eliminate duplicate bias.

### 5. Empirical Historical Priority Scoring
- Transparent preparation priority formula:
  $$\text{Priority Score} = \left(\frac{\text{Topic Frequency}}{\text{Max Topic Frequency}} \times 60\right) + \left(\frac{\text{Years Appeared}}{\text{Total Years}} \times 40\right)$$
- Categorizes topics into **Very High Priority** ($\ge 75$), **High Priority** ($\ge 50$), **Medium Priority** ($\ge 25$), and **Low Priority** ($< 25$).
- Connects historical exam questions to each prioritized topic with revision strategies.

### 6. AI Revision Roadmap & Spaced Study Planner
- Calculates day-by-day revision schedules weighted by topic priority scores.
- Students pick their target exam date and daily study capacity.
- Sequences high-yield core topics first, with spaced reinforcement days and final mock exam simulations.

### 7. University Mock Exam Generator
- Assembles realistic, balanced practice examination papers from the question bank.
- Supports 50, 75, or 100 marks and 2 or 3-hour durations.
- Displays an authentic university exam container with instructions and marks distribution.

### 8. Cross-Year Question Similarity Matcher
- Computes token-set Jaccard similarity across questions from different academic years.
- Detects questions asked in nearly identical wording (e.g. 2022 vs 2024), uncovering examiner templates.

### 9. Active Recall Flashcard Mode
- Self-assessment flashcards with flip-to-reveal metadata for practicing retrieval without viewing classifications upfront.

### 10. Multi-Format Report Center
- **PDF Report**: Publication-ready document generated with **ReportLab** containing metadata, KPIs, topic frequency tables, priority recommendations, and legal disclaimers.
- **Excel Report (.xlsx)**: 5 formatted worksheets (*Summary, Topic Frequency, Priority Recommendations, Year Distribution, Question Bank*).
- **CSV & JSON**: Separate datasets for questions and topic frequencies.

---

## 🏗️ Architecture & Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend & UI** | Streamlit (1.36+ `st.navigation`), Custom CSS, Plus Jakarta Sans, JetBrains Mono |
| **Interactive Charts** | Plotly Express & Plotly Graph Objects |
| **Data Engine** | Pandas, NumPy |
| **Document Processing** | PyMuPDF (`fitz`), python-docx, pytesseract, Pillow |
| **AI / NLP** | OpenAI API (Structured JSON Mode) + Deterministic Taxonomy NLP Engine |
| **Database** | SQLite3 (Foreign Keys, Indexes, Cascade Deletes) |
| **Report Generation** | ReportLab (PDF), openpyxl (Excel), CSV, JSON |
| **Testing** | pytest (16 automated tests) |

---

## 📂 Project Directory Structure

```
Previous-Year-Bot/
├── app.py                       # Main application entrypoint (st.navigation)
├── config.py                    # Global paths, weights, and LLM configuration
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore specifications
├── README.md                    # Project documentation
│
├── .streamlit/
│   └── config.toml              # Streamlit high-contrast light theme configuration
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
│   ├── priority_predictor.py    # Priority formula scoring & study recommendations
│   ├── visualization.py         # Interactive Plotly chart builders
│   ├── report_generator.py      # PDF, Excel, CSV, and JSON report generator
│   ├── study_planner.py         # Priority-weighted revision schedule generator
│   ├── mock_exam_generator.py   # Balanced practice examination paper synthesizer
│   └── similarity_engine.py     # Cross-year Jaccard question similarity matcher
│
├── views/
│   ├── dashboard.py             # Executive KPI overview & recurrence charts
│   ├── upload.py                # Drag-and-drop document upload pipeline
│   ├── question_analysis.py     # Detailed question cards & inline editor
│   ├── topic_frequency.py       # Full frequency rankings & topic comparator
│   ├── year_analysis.py         # Multi-year heatmaps & trajectory charts
│   ├── important_topics.py      # Prioritized study tiers & past questions
│   ├── question_bank.py         # Searchable question repository & flashcards
│   ├── study_planner.py         # AI study schedule, mock exams, and patterns
│   ├── export_reports.py        # Report downloads (PDF, Excel, CSV, JSON)
│   └── settings.py              # LLM credentials, model picker, DB management
│
├── utils/
│   ├── helpers.py               # SHA-256 duplicate hashing, formatting, text cleaning
│   ├── validators.py            # Upload validation, format & size checks
│   └── styling.py               # Custom CSS injector, KPI cards, badges, spotlight
│
├── assets/
│   └── custom.css               # Modern UI styling, high-contrast dark/light mode
│
├── sample_data/
│   ├── DBMS_PYQ_2022.txt        # Synthetic DBMS exam paper (2022)
│   ├── DBMS_PYQ_2023.txt        # Synthetic DBMS exam paper (2023)
│   ├── DBMS_PYQ_2024.txt        # Synthetic DBMS exam paper (2024)
│   └── seed_data.py             # Automatic sample database preloader
│
├── uploads/                     # Upload staging directory
├── exports/                     # Report export output directory
│
└── tests/
    ├── conftest.py              # Test configuration & path resolver
    ├── test_extraction.py       # Unit tests for text & question extraction
    ├── test_analyzer.py         # Unit tests for frequency & priority formula
    ├── test_classifier.py       # Unit tests for taxonomy mapping & JSON validation
    ├── test_study_planner.py    # Unit tests for revision roadmap allocation
    ├── test_mock_exam.py        # Unit tests for mock paper assembly
    └── test_similarity.py       # Unit tests for cross-year similarity matching
```

---

## 🚀 Quick Start & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/RahulGehlot14/Previous-Year-Bot.git
cd Previous-Year-Bot
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure OpenAI API Key
```bash
cp .env.example .env
```
Open `.env` and set your key:
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```
> **Note:** An API key is completely optional. If omitted, the application runs in **Rule-Based Demo Mode** with high-accuracy domain taxonomies.

### 5. Launch the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧭 Application Walkthrough

1. **Dashboard**: High-level KPIs, topic distribution pie chart, top recurring topic spotlight banner, and annual trajectory line charts.
2. **One-Click Demo Data**: Click **"🚀 Load Sample DBMS Dataset"** to immediately index 36 questions across 3 years of DBMS past papers.
3. **Upload Papers**: Drag and drop your own `.pdf`, `.docx`, or `.txt` exam papers with automated extraction and duplicate detection.
4. **Question Analysis**: Inspect questions with Bloom's taxonomy tags, marks, and inline editing.
5. **Topic Frequency**: Review frequency rankings and use the **Side-by-Side Topic Comparator** to compare any 2-5 topics.
6. **Year-wise Analysis**: Explore topic intensity heatmaps across consecutive exam cycles.
7. **Important Topics**: Review high-yield priority tiers and associated previous-year questions.
8. **Question Bank**: Search questions by keyword or switch to **Active Recall Flashcard Mode**.
9. **Study Planner & Mock Exam**: Generate a weighted revision schedule and create a printable practice exam paper.
10. **Export Reports**: Download publication-ready PDF reports, multi-sheet Excel workbooks, CSVs, and JSON.

---

## 🧪 Testing & Quality Assurance

Run the full automated test suite (16 tests):
```bash
pytest -v
```

Output:
```
tests/test_analyzer.py::test_topic_frequency_aggregation PASSED          [  6%]
tests/test_analyzer.py::test_priority_score_formula PASSED               [ 12%]
tests/test_analyzer.py::test_year_wise_distribution_matrix PASSED        [ 18%]
tests/test_classifier.py::test_rule_based_normalization_classification PASSED [ 25%]
tests/test_classifier.py::test_multi_year_topic_consistency PASSED       [ 31%]
tests/test_classifier.py::test_transaction_concurrency_classification PASSED [ 37%]
tests/test_classifier.py::test_safe_json_loads_markdown_fences PASSED    [ 43%]
tests/test_extraction.py::test_question_extraction_counts PASSED         [ 50%]
tests/test_extraction.py::test_marks_extraction PASSED                   [ 56%]
tests/test_extraction.py::test_clean_text_preserves_question_content PASSED [ 62%]
tests/test_extraction.py::test_empty_document_handling PASSED            [ 68%]
tests/test_mock_exam.py::test_mock_paper_generation PASSED               [ 75%]
tests/test_similarity.py::test_jaccard_similarity_calculation PASSED     [ 81%]
tests/test_similarity.py::test_dissimilar_questions PASSED               [ 87%]
tests/test_similarity.py::test_find_cross_year_duplicates PASSED         [ 93%]
tests/test_study_planner.py::test_study_plan_generation PASSED           [100%]
======================== 16 passed in 2.93s ========================
```

---

## 📤 Pushing to GitHub

To push commits to your remote repository:

```bash
git add .
git commit -m "docs: comprehensive README and project documentation"
git push -u origin main
```

---

## 🛡️ Security & Compliance

- **No Hardcoded Secrets**: Credentials are read from `.env` or session state and never committed to version control.
- **SQL Injection Prevention**: All queries use parameterized placeholders (`?`).
- **File Validation**: MIME types, extensions, and file sizes are verified prior to ingestion.
- **Educational Disclaimer**: Priority rankings reflect empirical historical trends to aid study time allocation and do not guarantee future examination questions.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
