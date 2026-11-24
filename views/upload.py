"""
Upload Question Papers View for Previous Year Question Paper Analyzer.
Handles batch file uploads, validation, duplicate detection, text extraction,
and AI/rule-based topic classification.
"""

import streamlit as st
from datetime import datetime
from database.db_manager import DatabaseManager
from modules.document_processor import DocumentProcessor
from modules.question_extractor import QuestionExtractor
from modules.ai_classifier import AIClassifier
from utils.helpers import compute_file_hash, format_bytes
from utils.validators import validate_uploaded_file
from utils.styling import render_section_header, load_custom_css
from config import DEFAULT_SUBJECTS, SUPPORTED_FORMATS

def render():
    load_custom_css()

    if "db_manager" not in st.session_state:
        st.session_state["db_manager"] = DatabaseManager()
    db: DatabaseManager = st.session_state["db_manager"]

    render_section_header("Upload Question Papers", "Ingest past university examination papers to extract, separate, and classify questions", "📤")

    # Form metadata inputs
    col_sub, col_yr = st.columns([2, 1])

    with col_sub:
        subject_options = [s for s in DEFAULT_SUBJECTS if s != "Other / Custom Subject"]
        subject_choice = st.selectbox(
            "Select Subject",
            options=subject_options + ["Enter Custom Subject..."],
            index=0
        )
        if subject_choice == "Enter Custom Subject...":
            custom_sub = st.text_input("Enter Subject Name", placeholder="e.g. Microprocessors & Interfacing")
            chosen_subject = custom_sub.strip() if custom_sub.strip() else "General Subject"
        else:
            chosen_subject = subject_choice

    with col_yr:
        current_year = datetime.now().year
        year_options = [str(y) for y in range(current_year, current_year - 10, -1)]
        academic_year = st.selectbox("Academic Year", options=year_options, index=1)

    # File Uploader
    uploaded_files = st.file_uploader(
        f"Drag and drop question papers ({', '.join(SUPPORTED_FORMATS)})",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        help="Upload past examination papers. Scanned image PDFs will use OCR fallback."
    )

    if uploaded_files:
        st.markdown(f"**Selected {len(uploaded_files)} file(s):**")
        files_info = []
        for f in uploaded_files:
            files_info.append({
                "Filename": f.name,
                "Size": format_bytes(f.size),
                "Format": f.name.split(".")[-1].upper()
            })
        st.table(files_info)

        use_llm = st.checkbox(
            "Enable OpenAI AI Classification (Requires OpenAI API Key in Settings or .env)",
            value=bool(st.session_state.get("openai_api_key")),
            help="If unchecked, PYQ Analyzer uses the high-speed, deterministic Rule-Based Demo Mode."
        )

        if st.button("🚀 Process & Analyze Uploaded Papers", type="primary", use_container_width=True):
            api_key = st.session_state.get("openai_api_key", "")
            classifier = AIClassifier(api_key=api_key if use_llm else None)

            progress_bar = st.progress(0.0)
            status_text = st.empty()

            total_files = len(uploaded_files)
            successfully_processed = 0
            total_questions_extracted = 0
            duplicates_skipped = 0

            for idx, uploaded_file in enumerate(uploaded_files):
                file_bytes = uploaded_file.read()
                filename = uploaded_file.name

                status_text.text(f"Processing ({idx+1}/{total_files}): {filename}...")

                # 1. Validation
                is_valid, err_msg = validate_uploaded_file(filename, file_bytes)
                if not is_valid:
                    st.error(f"❌ '{filename}': {err_msg}")
                    continue

                # 2. Duplicate Detection
                f_hash = compute_file_hash(file_bytes)
                if db.paper_exists_by_hash(f_hash):
                    st.warning(f"⚠️ '{filename}' has already been uploaded previously. Skipped to prevent duplicate counts.")
                    duplicates_skipped += 1
                    continue

                # 3. Text Extraction
                try:
                    text, meta = DocumentProcessor.extract_text(file_bytes, filename)
                    if meta.get("ocr_warning"):
                        st.info(f"ℹ️ '{filename}': {meta['ocr_warning']}")
                except Exception as e:
                    st.error(f"❌ Failed to extract text from '{filename}': {str(e)}")
                    continue

                # 4. Question Extraction
                questions = QuestionExtractor.extract_questions(
                    text=text,
                    filename=filename,
                    subject=chosen_subject,
                    academic_year=academic_year
                )

                if not questions:
                    st.warning(f"⚠️ Could not identify discrete questions in '{filename}'. Please ensure questions are numbered.")
                    continue

                # 5. Insert Paper Record
                file_ext = filename.split(".")[-1].lower()
                paper_id = db.insert_paper(
                    filename=filename,
                    file_hash=f_hash,
                    file_size=len(file_bytes),
                    file_type=file_ext,
                    subject=chosen_subject,
                    academic_year=academic_year
                )

                for q in questions:
                    q["paper_id"] = paper_id

                # 6. Classification
                status_text.text(f"Classifying {len(questions)} questions for '{filename}'...")
                classified_questions = classifier.classify_questions(questions)

                # 7. Database Batch Insert
                db.insert_questions_batch(classified_questions)
                db.update_paper_question_count(paper_id, len(classified_questions))

                successfully_processed += 1
                total_questions_extracted += len(classified_questions)
                progress_bar.progress((idx + 1) / total_files)

            status_text.empty()
            progress_bar.progress(1.0)

            if successfully_processed > 0:
                st.success(
                    f"🎉 Successfully processed {successfully_processed} paper(s)! "
                    f"Extracted and classified {total_questions_extracted} questions for **{chosen_subject}** ({academic_year})."
                )
                col_view1, col_view2 = st.columns(2)
                with col_view1:
                    if st.button("🔍 View Question Analysis", key="btn_view_analysis", use_container_width=True):
                        st.switch_page("views/question_analysis.py")
                with col_view2:
                    if st.button("📊 View Topic Frequencies", key="btn_view_freq", use_container_width=True):
                        st.switch_page("views/topic_frequency.py")
            elif duplicates_skipped > 0:
                st.info("No new papers were processed because identical documents were already present in the database.")

    # Currently uploaded papers table with delete action
    st.markdown("<br>", unsafe_allow_html=True)
    render_section_header("Indexed Question Papers in Database", "View and manage uploaded papers", "🗄️")
    existing_papers = db.get_papers()
    if existing_papers:
        for p in existing_papers:
            with st.expander(f"📄 {p['filename']} — {p['subject']} ({p['academic_year']}) — {p['question_count']} questions"):
                col_info, col_del = st.columns([4, 1])
                with col_info:
                    st.write(f"**Size:** {format_bytes(p['file_size'])} | **Uploaded:** {p['uploaded_at']} | **Type:** {p['file_type'].upper()}")
                with col_del:
                    if st.button("🗑️ Delete Paper", key=f"del_paper_{p['id']}", type="secondary"):
                        db.delete_paper(p["id"])
                        st.success(f"Deleted '{p['filename']}' and its associated questions.")
                        st.rerun()
    else:
        st.write("No papers in database yet.")

if __name__ == "__main__" or True:
    render()
