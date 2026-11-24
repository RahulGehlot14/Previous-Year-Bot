-- SQLite Schema for Previous Year Question Paper Analyzer (PYQ Analyzer)

-- 1. Papers Table
CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    file_hash TEXT UNIQUE NOT NULL,
    file_size INTEGER NOT NULL,
    file_type TEXT NOT NULL,
    subject TEXT NOT NULL,
    academic_year TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    question_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'processed'
);

-- 2. Questions Table
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT NOT NULL,
    paper_id INTEGER NOT NULL,
    question_number TEXT,
    question_text TEXT NOT NULL,
    marks REAL DEFAULT NULL,
    subject TEXT NOT NULL,
    academic_year TEXT NOT NULL,
    source_document TEXT NOT NULL,
    unit TEXT DEFAULT 'General',
    topic TEXT DEFAULT 'Unclassified',
    subtopic TEXT DEFAULT '',
    keywords TEXT DEFAULT '[]',
    question_type TEXT DEFAULT 'Theory',
    difficulty TEXT DEFAULT 'Medium',
    bloom_level TEXT DEFAULT 'Understand',
    classification_source TEXT DEFAULT 'rule_based',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE
);

-- 3. Topics Master Table
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    topic_name TEXT NOT NULL,
    unit TEXT DEFAULT 'General',
    description TEXT DEFAULT '',
    UNIQUE(subject, topic_name)
);

-- 4. Analysis Results Cache Table
CREATE TABLE IF NOT EXISTS analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    topic TEXT NOT NULL,
    unit TEXT DEFAULT 'General',
    frequency INTEGER DEFAULT 0,
    years_appeared INTEGER DEFAULT 0,
    papers_count INTEGER DEFAULT 0,
    frequency_pct REAL DEFAULT 0.0,
    priority_score REAL DEFAULT 0.0,
    priority_category TEXT DEFAULT 'Low Priority',
    last_calculated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(subject, topic)
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_questions_paper_id ON questions(paper_id);
CREATE INDEX IF NOT EXISTS idx_questions_subject ON questions(subject);
CREATE INDEX IF NOT EXISTS idx_questions_topic ON questions(topic);
CREATE INDEX IF NOT EXISTS idx_questions_year ON questions(academic_year);
CREATE INDEX IF NOT EXISTS idx_papers_hash ON papers(file_hash);
