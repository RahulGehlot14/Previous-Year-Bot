"""
Report Generator Module for Previous Year Question Paper Analyzer.
Generates comprehensive exportable reports in multiple formats:
- PDF (via ReportLab, with metadata, tables, priority recommendations, and legal disclaimer)
- Excel (.xlsx via openpyxl with multiple formatted worksheets)
- CSV (Questions dataset and Topic frequency summary)
- JSON (Classified questions schema)
"""

import io
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class ReportGenerator:
    """Generates downloadable reports across PDF, Excel, CSV, and JSON."""

    @staticmethod
    def generate_csv_questions(questions: List[Dict[str, Any]]) -> str:
        """Converts questions list to CSV string."""
        if not questions:
            return ""
        df = pd.DataFrame(questions)
        # Format list keywords to comma-separated string
        if "keywords" in df.columns:
            df["keywords"] = df["keywords"].apply(lambda k: ", ".join(k) if isinstance(k, list) else str(k))
        return df.to_csv(index=False)

    @staticmethod
    def generate_csv_topics(topics_summary_df: pd.DataFrame) -> str:
        """Converts topic frequency summary DataFrame to CSV string."""
        if topics_summary_df.empty:
            return ""
        return topics_summary_df.to_csv(index=False)

    @staticmethod
    def generate_json_questions(questions: List[Dict[str, Any]]) -> str:
        """Serializes questions list into formatted JSON."""
        return json.dumps(questions, indent=2, default=str)

    @staticmethod
    def generate_excel_report(questions: List[Dict[str, Any]],
                              topic_summary_df: pd.DataFrame,
                              priorities_df: pd.DataFrame,
                              year_distribution_df: pd.DataFrame) -> bytes:
        """
        Creates a structured multi-worksheet Excel workbook:
        - Executive Summary
        - Topic Frequency
        - Priority Recommendations
        - Year-wise Distribution
        - Full Question Bank
        """
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Sheet 1: Executive Summary Metrics
            summary_data = {
                "Metric": [
                    "Report Generated At",
                    "Total Questions Analyzed",
                    "Unique Topics Identified",
                    "Total Papers Analyzed"
                ],
                "Value": [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    len(questions),
                    topic_summary_df["Topic"].nunique() if not topic_summary_df.empty else 0,
                    pd.DataFrame(questions)["source_document"].nunique() if questions else 0
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)

            # Sheet 2: Topic Frequency
            if not topic_summary_df.empty:
                topic_summary_df.to_excel(writer, sheet_name="Topic Frequency", index=False)

            # Sheet 3: Priority Recommendations
            if not priorities_df.empty:
                priorities_df.to_excel(writer, sheet_name="Priority Recommendations", index=False)

            # Sheet 4: Year-wise Distribution
            if not year_distribution_df.empty:
                year_distribution_df.to_excel(writer, sheet_name="Year Distribution")

            # Sheet 5: Questions Bank
            if questions:
                q_df = pd.DataFrame(questions)
                if "keywords" in q_df.columns:
                    q_df["keywords"] = q_df["keywords"].apply(lambda k: ", ".join(k) if isinstance(k, list) else str(k))
                q_df.to_excel(writer, sheet_name="Question Bank", index=False)

        return output.getvalue()

    @staticmethod
    def generate_pdf_report(subject: str,
                            kpis: Dict[str, Any],
                            topic_summary_df: pd.DataFrame,
                            priorities_df: pd.DataFrame) -> bytes:
        """
        Generates a comprehensive academic PDF report using ReportLab:
        - Professional Header Banner
        - Analysis Metadata Table
        - Key KPI Metrics
        - Topic Frequency Table
        - Top Priority Topics Table
        - Strategic Preparation Recommendations
        - Mandatory Historical Trends Disclaimer
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom typography styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1E3A8A"),
            spaceAfter=6
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#475569"),
            spaceAfter=14
        )
        section_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1E40AF"),
            spaceBefore=14,
            spaceAfter=8
        )
        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#1E293B")
        )
        table_cell_style = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#1E293B")
        )
        table_header_style = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            fontName="Helvetica-Bold",
            textColor=colors.white
        )
        disclaimer_style = ParagraphStyle(
            "Disclaimer",
            parent=styles["Italic"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#64748B")
        )

        story = []

        # 1. Title Banner
        story.append(Paragraph("Previous Year Question Paper Analysis Report", title_style))
        story.append(Paragraph(
            f"Subject: <b>{subject or 'All Analyzed Subjects'}</b> | Generated on: {datetime.now().strftime('%B %d, %Y')}",
            subtitle_style
        ))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceAfter=14))

        # 2. Executive KPI Summary Table
        story.append(Paragraph("1. Executive Summary & KPIs", section_style))
        kpi_data = [
            [
                Paragraph("<b>Total Papers Analyzed:</b>", body_style),
                Paragraph(str(kpis.get("total_papers", 0)), body_style),
                Paragraph("<b>Total Questions Extracted:</b>", body_style),
                Paragraph(str(kpis.get("total_questions", 0)), body_style)
            ],
            [
                Paragraph("<b>Unique Topics Identified:</b>", body_style),
                Paragraph(str(kpis.get("unique_topics", 0)), body_style),
                Paragraph("<b>Years Covered:</b>", body_style),
                Paragraph(str(kpis.get("total_years", 0)), body_style)
            ],
            [
                Paragraph("<b>Most Repeated Topic:</b>", body_style),
                Paragraph(str(kpis.get("most_repeated_topic", "None")), body_style),
                Paragraph("<b>Occurrences:</b>", body_style),
                Paragraph(f"{kpis.get('most_repeated_count', 0)} times", body_style)
            ]
        ]
        kpi_table = Table(kpi_data, colWidths=[130, 140, 140, 130])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 14))

        # 3. Top Topics Frequency Table
        story.append(Paragraph("2. Top Frequently Asked Topics", section_style))
        if not topic_summary_df.empty:
            table_rows = [[
                Paragraph("Topic Name", table_header_style),
                Paragraph("Unit", table_header_style),
                Paragraph("Questions", table_header_style),
                Paragraph("Years Appeared", table_header_style),
                Paragraph("Frequency %", table_header_style)
            ]]

            for _, r in topic_summary_df.head(10).iterrows():
                table_rows.append([
                    Paragraph(str(r["Topic"]), table_cell_style),
                    Paragraph(str(r["Unit"]), table_cell_style),
                    Paragraph(str(r["Frequency"]), table_cell_style),
                    Paragraph(str(r["Years Appeared"]), table_cell_style),
                    Paragraph(f"{r['Frequency %']}%", table_cell_style)
                ])

            freq_table = Table(table_rows, colWidths=[200, 80, 80, 90, 90])
            freq_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(freq_table)
        else:
            story.append(Paragraph("No topic frequency data available.", body_style))

        story.append(Spacer(1, 14))

        # 4. Priority Recommendations Table
        story.append(Paragraph("3. Examination Preparation Priority Recommendations", section_style))
        if not priorities_df.empty:
            p_rows = [[
                Paragraph("Topic", table_header_style),
                Paragraph("Priority Score", table_header_style),
                Paragraph("Category", table_header_style),
                Paragraph("Preparation Recommendation", table_header_style)
            ]]

            for _, r in priorities_df.head(8).iterrows():
                p_rows.append([
                    Paragraph(str(r["Topic"]), table_cell_style),
                    Paragraph(f"{r['Priority Score']} / 100", table_cell_style),
                    Paragraph(str(r["Priority Category"]), table_cell_style),
                    Paragraph(str(r.get("Preparation Advice", "")), table_cell_style)
                ])

            p_table = Table(p_rows, colWidths=[150, 75, 95, 220])
            p_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#065F46")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#ECFDF5")]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#A7F3D0")),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(p_table)
        else:
            story.append(Paragraph("No priority recommendation data available.", body_style))

        story.append(Spacer(1, 18))

        # 5. Mandatory Historical Disclaimer
        story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#94A3B8"), spaceAfter=10))
        disclaimer_text = (
            "<b>Disclaimer:</b> These priority scores, frequency analytics, and topic rankings are derived strictly "
            "from historical examination question patterns. They are intended as an analytical revision aid to help "
            "students allocate study time efficiently and do not constitute an official prediction or guarantee of "
            "questions appearing on future examinations."
        )
        story.append(Paragraph(disclaimer_text, disclaimer_style))

        doc.build(story)
        return buffer.getvalue()
