def get_html_report_template(
    total_people,
    analysis_date,
    summary_table_html,
    dichotomy_table_html,
    dominant_table_html,
    individual_table_html,
):
    """Generate HTML report template with embedded styles."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            .section {{ margin: 30px 0; }}
            h2 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
            .summary {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>MBTI Analysis Report</h1>

        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Total Participants:</strong> {total_people}</p>
            <p><strong>Analysis Date:</strong> {analysis_date}</p>
        </div>

        <div class="section">
            <h2>MBTI Type Distribution</h2>
            {summary_table_html}
        </div>

        <div class="section">
            <h2>Dichotomy Analysis</h2>
            {dichotomy_table_html}
        </div>

        <div class="section">
            <h2>Dominant Function Analysis</h2>
            {dominant_table_html}
        </div>

        <div class="section">
            <h2>Individual Results</h2>
            {individual_table_html}
        </div>
    </body>
    </html>
    """


CSS_BORDER_COLOR = "#ddd"
CSS_HEADER_BG_COLOR = "#f2f2f2"
CSS_SECTION_COLOR = "#333"
CSS_BORDER_BOTTOM_COLOR = "#4CAF50"
CSS_SUMMARY_BG_COLOR = "#f9f9f9"
