"""
Custom CSS styling and UI layout helper components for Streamlit.
Provides light/dark mode styling, professional cards, KPI badges, typography,
flashcards, and revision timeline nodes.
"""

import streamlit as st
from typing import Any, Dict
from config import BASE_DIR

CSS_PATH = BASE_DIR / "assets" / "custom.css"

def load_custom_css():
    """Loads and injects custom CSS stylesheet into Streamlit."""
    if CSS_PATH.exists():
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

def render_kpi_card(title: str, value: Any, subtitle: str = "", icon: str = "📊", delta: str = None):
    """Renders a polished, overflow-safe KPI card."""
    delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ''
    
    # Check if value is a long text or number to prevent word collapsing
    val_str = str(value)
    is_text = len(val_str) > 6 or any(c.isalpha() for c in val_str)
    val_class = "kpi-value-text" if is_text else "kpi-value-num"

    card_html = f"""
    <div class="kpi-card">
        <div class="kpi-header">
            <span class="kpi-icon">{icon}</span>
            <span class="kpi-title">{title}</span>
        </div>
        <div class="kpi-value {val_class}" title="{val_str}">{val_str}</div>
        <div class="kpi-subtitle">{subtitle}</div>
        {delta_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def render_topic_spotlight(topic: str, count: int, years: int, total_q: int):
    """Renders a prominent, beautifully aligned spotlight card for the most repeated topic."""
    pct = round((count / max(1, total_q)) * 100, 1)
    spotlight_html = f"""
    <div class="spotlight-card">
        <div class="spotlight-badge">🔥 #1 Top Recurring Examination Topic</div>
        <div class="spotlight-title">{topic}</div>
        <div class="spotlight-stats">
            <span class="spotlight-stat-item"><b>{count}</b> questions asked</span>
            <span class="spotlight-dot">•</span>
            <span class="spotlight-stat-item">Appeared in <b>{years}</b> distinct exam years</span>
            <span class="spotlight-dot">•</span>
            <span class="spotlight-stat-item"><b>{pct}%</b> of total curriculum questions</span>
        </div>
    </div>
    """
    st.markdown(spotlight_html, unsafe_allow_html=True)

def get_priority_badge_html(category: str) -> str:
    """Returns styled HTML badge for priority categories."""
    cat_lower = str(category).lower().replace(" ", "-")
    if "very-high" in cat_lower:
        badge_class = "badge-very-high"
    elif "high" in cat_lower:
        badge_class = "badge-high"
    elif "medium" in cat_lower:
        badge_class = "badge-medium"
    else:
        badge_class = "badge-low"

    return f'<span class="priority-badge {badge_class}">{category}</span>'

def render_section_header(title: str, subtitle: str = "", icon: str = ""):
    """Renders a clean section header with optional icon and subtitle."""
    icon_str = f"{icon} " if icon else ""
    st.markdown(f"""
    <div class="section-header-box">
        <h2 class="section-title">{icon_str}{title}</h2>
        {f'<p class="section-subtitle">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def render_flashcard(question: Dict[str, Any], show_answer: bool = False):
    """Renders an interactive revision flashcard."""
    marks_str = f"[{question.get('marks')} Marks]" if question.get('marks') else ""
    card_html = f"""
    <div class="flashcard-box">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-weight: 700; font-size: 0.85rem; color: #2563EB;">{question.get('academic_year', '')} • {question.get('question_number', '')}</span>
            <span style="font-size: 0.82rem; font-weight: 600; color: #64748B;">{marks_str}</span>
        </div>
        <div class="flashcard-q">{question.get('question_text', '')}</div>
        <div class="flashcard-meta">
            <span class="meta-chip">Unit: {question.get('unit', 'General')}</span>
            <span class="meta-chip">Topic: {question.get('topic', 'Unclassified')}</span>
            <span class="meta-chip">Bloom: {question.get('bloom_level', 'Understand')}</span>
            <span class="meta-chip">Difficulty: {question.get('difficulty', 'Medium')}</span>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def render_timeline_node(day_label: str, title: str, details: str, badge_html: str = ""):
    """Renders an interactive timeline entry for study plans."""
    node_html = f"""
    <div class="timeline-card">
        <div class="timeline-day">{day_label}</div>
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div class="timeline-title">{title}</div>
            {badge_html}
        </div>
        <div class="timeline-details">{details}</div>
    </div>
    """
    st.markdown(node_html, unsafe_allow_html=True)
