import openpyxl
from openpyxl.chart import PieChart, Reference, BarChart
from openpyxl.chart.series import SeriesLabel
from openpyxl.chart.label import DataLabelList
import openpyxl.chart.text
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.styles import Font, PatternFill
from openpyxl.drawing.line import LineProperties
from openpyxl.chart.layout import Layout, ManualLayout
from consts import mbti_colors, MBTI_TYPES


def create_distribution_charts(workbook):
    # Create or get the data sheet
    if 'Data' in workbook.sheetnames:
        data_sheet = workbook['Data']
    else:
        data_sheet = workbook.create_sheet(title="Data")

    # Create or get the dashboard sheet for charts
    if 'Dashboard' in workbook.sheetnames:
        chart_sheet = workbook['Dashboard']
    else:
        chart_sheet = workbook.create_sheet(title="Dashboard")

    # Clear any existing charts
    chart_sheet._charts = []

    # Add a title to the dashboard
    chart_sheet['K1'] = "MBTI Distribution Dashboard"
    chart_sheet['K1'].font = Font(bold=True, size=16)

    # Prepare data in the data sheet
    prepare_main_distribution_data(data_sheet)
    prepare_dichotomy_data(data_sheet)
    prepare_external_internal_data(data_sheet)
    prepare_dominant_function_data(data_sheet)

    # Create charts in the dashboard sheet
    create_main_distribution_chart(data_sheet, chart_sheet)
    create_dichotomy_charts(data_sheet, chart_sheet)
    create_external_internal_charts(data_sheet, chart_sheet)
    create_facet_bar_charts(data_sheet, chart_sheet)
    create_dominant_chart(data_sheet, chart_sheet)

    # Adjust column widths for data sheet
    adjust_column_widths(data_sheet)

    # Hide gridlines in the dashboard for a cleaner look
    chart_sheet.sheet_view.showGridLines = False

    # Reorder sheets to put Dashboard first
    # reorder_sheets(workbook)

    # if 'Dashboard' in workbook.sheetnames:
    #     reset_column_widths(workbook['Dashboard'])

    # create_dashboard_frame(chart_sheet)


def prepare_main_distribution_data(data_sheet):
    # Write headers
    data_sheet['A1'] = "MBTI Type Data"
    data_sheet['A1'].font = Font(bold=True)

    # Write MBTI types and count formulas
    for row, mbti_type in enumerate(MBTI_TYPES, start=2):
        data_sheet[f'A{row}'] = mbti_type
        data_sheet[f'B{row}'] = f"=COUNTIF(Table1[Type],A{row})"
        if mbti_type in mbti_colors:
            data_sheet[f'A{row}'].fill = PatternFill(start_color=mbti_colors[mbti_type],
                                                     end_color=mbti_colors[mbti_type],
                                                     fill_type="solid")


def prepare_dichotomy_data(data_sheet):
    data_sheet['D1'] = "Dichotomies Data"
    data_sheet['D1'].font = Font(bold=True)
    data_sheet['E2'] = "Count"
    data_sheet['E2'].font = Font(bold=True)

    # Define dichotomy colors - using professional color scheme
    dichotomy_colors = {
        "Extroversion": "4472C4",  # Blue
        "Introversion": "ED7D31",  # Orange
        "Sensing": "70AD47",  # Green
        "Intuition": "FFC000",  # Gold
        "Thinking": "5B9BD5",  # Light Blue
        "Feeling": "A5A5A5",  # Gray
        "Judging": "9966FF",  # Purple
        "Perceiving": "4BACC6"  # Teal
    }

    # Energy source - E/I
    data_sheet['D2'] = "Energy source - E/I"
    data_sheet['D2'].font = Font(bold=True)
    data_sheet['D3'] = "Extroversion"
    data_sheet['E3'] = "Introversion"
    data_sheet['D4'] = "=COUNTIF(Table1[Type], \"*E*\")"
    data_sheet['E4'] = "=COUNTIF(Table1[Type], \"*I*\")"
    data_sheet['D3'].fill = PatternFill(start_color=dichotomy_colors["Extroversion"],
                                        end_color=dichotomy_colors["Extroversion"], fill_type="solid")
    data_sheet['E3'].fill = PatternFill(start_color=dichotomy_colors["Introversion"],
                                        end_color=dichotomy_colors["Introversion"], fill_type="solid")

    # Information - S/N
    data_sheet['D6'] = "Information - S/N"
    data_sheet['D6'].font = Font(bold=True)
    data_sheet['D7'] = "Sensing"
    data_sheet['E7'] = "Intuition"
    data_sheet['D8'] = "=COUNTIF(Table1[Type], \"*S*\")"
    data_sheet['E8'] = "=COUNTIF(Table1[Type], \"*N*\")"
    data_sheet['D7'].fill = PatternFill(start_color=dichotomy_colors["Sensing"],
                                        end_color=dichotomy_colors["Sensing"], fill_type="solid")
    data_sheet['E7'].fill = PatternFill(start_color=dichotomy_colors["Intuition"],
                                        end_color=dichotomy_colors["Intuition"], fill_type="solid")

    # Decisions - T/F
    data_sheet['D10'] = "Decisions - T/F"
    data_sheet['D10'].font = Font(bold=True)
    data_sheet['D11'] = "Thinking"
    data_sheet['E11'] = "Feeling"
    data_sheet['D12'] = "=COUNTIF(Table1[Type], \"*T*\")"
    data_sheet['E12'] = "=COUNTIF(Table1[Type], \"*F*\")"
    data_sheet['D11'].fill = PatternFill(start_color=dichotomy_colors["Thinking"],
                                        end_color=dichotomy_colors["Thinking"], fill_type="solid")
    data_sheet['E11'].fill = PatternFill(start_color=dichotomy_colors["Feeling"],
                                         end_color=dichotomy_colors["Feeling"], fill_type="solid")

    # Lifestyle - J/P
    data_sheet['D14'] = "Lifestyle - J/P"
    data_sheet['D14'].font = Font(bold=True)
    data_sheet['D15'] = "Judging"
    data_sheet['E15'] = "Perceiving"
    data_sheet['D16'] = "=COUNTIF(Table1[Type], \"*J*\")"
    data_sheet['E16'] = "=COUNTIF(Table1[Type], \"*P*\")"
    data_sheet['D15'].fill = PatternFill(start_color=dichotomy_colors["Judging"],
                                         end_color=dichotomy_colors["Judging"], fill_type="solid")
    data_sheet['E15'].fill = PatternFill(start_color=dichotomy_colors["Perceiving"],
                                         end_color=dichotomy_colors["Perceiving"], fill_type="solid")

    # Calculate percentages for E/I
    data_sheet['D5'] = f"=(D4/SUM(D4:E4))"
    data_sheet['E5'] = f"=(E4/SUM(D4:E4))"
    data_sheet['D5'].number_format = "0.0%"
    data_sheet['E5'].number_format = "0.0%"
    # Calculate percentages for S/N
    data_sheet['D9'] = f"=(D8/SUM(D8:E8))"
    data_sheet['E9'] = f"=(E8/SUM(D8:E8))"
    data_sheet['D9'].number_format = "0.0%"
    data_sheet['E9'].number_format = "0.0%"
    # Calculate percentages for T/F
    data_sheet['D13'] = f"=(D12/SUM(D12:E12))"
    data_sheet['E13'] = f"=(E12/SUM(D12:E12))"
    data_sheet['D13'].number_format = "0.0%"
    data_sheet['E13'].number_format = "0.0%"
    # Calculate percentages for J/P
    data_sheet['D17'] = f"=(D16/SUM(D16:E16))"
    data_sheet['E17'] = f"=(E16/SUM(D16:E16))"
    data_sheet['D17'].number_format = "0.0%"
    data_sheet['E17'].number_format = "0.0%"

    # calculate dichotomy preference
    data_sheet['D19'] = "Dichotomy Preference data"
    data_sheet['D19'].font = Font(bold=True)
    # titles Initiating-Receiving
    data_sheet['D20'] = "Initiating-Receiving"
    data_sheet['D20'].font = Font(bold=True)
    data_sheet['D21'] = "In preference (Initiating)"
    data_sheet['D22'] = "In preference (Receiving)"
    data_sheet['D23'] = "Out of preference (Initiating)"
    data_sheet['D24'] = "Out of preference (Receiving)"
    data_sheet['D25'] = "MIDZONE (Initiating-Receiving)"
    # data for Initiating-Receiving
    data_sheet['E21'] = '=COUNTIF(Table1[Initiating],"=IN-PREF")'
    data_sheet['E22'] = '=COUNTIF(Table1[Receiving],"=IN-PREF")'
    data_sheet['E23'] = '=COUNTIF(Table1[Initiating],"=OUT-OF-PREF")'
    data_sheet['E24'] = '=COUNTIF(Table1[Receiving],"=OUT-OF-PREF")'
    data_sheet['E25'] = '=COUNTIF(Table1[Initiating],"=MIDZONE")'
    # titles Initiating-Receiving
    data_sheet['D28'] = "Expressive-Contained"
    data_sheet['D28'].font = Font(bold=True)
    data_sheet['D29'] = "In preference (Expressive)"
    data_sheet['D30'] = "In preference (Contained)"
    data_sheet['D31'] = "Out of preference (Expressive)"
    data_sheet['D32'] = "Out of preference (Contained)"
    data_sheet['D33'] = "MIDZONE (Expressive-Contained)"
    # data for Initiating-Receiving
    data_sheet['E29'] = '=COUNTIF(Table1[Expressive],"=IN-PREF")'
    data_sheet['E30'] = '=COUNTIF(Table1[Contained],"=IN-PREF")'
    data_sheet['E31'] = '=COUNTIF(Table1[Expressive],"=OUT-OF-PREF")'
    data_sheet['E32'] = '=COUNTIF(Table1[Contained],"=OUT-OF-PREF")'
    data_sheet['E33'] = '=COUNTIF(Table1[Contained],"=MIDZONE")'
    # titles Gregarious-Intimate
    data_sheet['D36'] = "Gregarious-Intimate"
    data_sheet['D36'].font = Font(bold=True)
    data_sheet['D37'] = "In preference (Gregarious)"
    data_sheet['D38'] = "In preference (Intimate)"
    data_sheet['D39'] = "Out of preference (Gregarious)"
    data_sheet['D40'] = "Out of preference (Intimate)"
    data_sheet['D41'] = "MIDZONE (Gregarious-Intimate)"
    # data for Gregarious-Intimate
    data_sheet['E37'] = '=COUNTIF(Table1[Gregarious],"=IN-PREF")'
    data_sheet['E38'] = '=COUNTIF(Table1[Intimate],"=IN-PREF")'
    data_sheet['E39'] = '=COUNTIF(Table1[Gregarious],"=OUT-OF-PREF")'
    data_sheet['E40'] = '=COUNTIF(Table1[Intimate],"=OUT-OF-PREF")'
    data_sheet['E41'] = '=COUNTIF(Table1[Intimate],"=MIDZONE")'

    # titles Active-Reflective
    data_sheet['D44'] = "Active-Reflective"
    data_sheet['D44'].font = Font(bold=True)
    data_sheet['D45'] = "In preference (Active)"
    data_sheet['D46'] = "In preference (Reflective)"
    data_sheet['D47'] = "Out of preference (Active)"
    data_sheet['D48'] = "Out of preference (Reflective)"
    data_sheet['D49'] = "MIDZONE (Active-Reflective)"
    # data for Active-Reflective
    data_sheet['E45'] = '=COUNTIF(Table1[Active],"=IN-PREF")'
    data_sheet['E46'] = '=COUNTIF(Table1[Reflective],"=IN-PREF")'
    data_sheet['E47'] = '=COUNTIF(Table1[Active],"=OUT-OF-PREF")'
    data_sheet['E48'] = '=COUNTIF(Table1[Reflective],"=OUT-OF-PREF")'
    data_sheet['E49'] = '=COUNTIF(Table1[Reflective],"=MIDZONE")'

    # titles Enthusiastic-Quiet
    data_sheet['D52'] = "Enthusiastic-Quiet"
    data_sheet['D52'].font = Font(bold=True)
    data_sheet['D53'] = "In preference (Enthusiastic)"
    data_sheet['D54'] = "In preference (Quiet)"
    data_sheet['D55'] = "Out of preference (Enthusiastic)"
    data_sheet['D56'] = "Out of preference (Quiet)"
    data_sheet['D57'] = "MIDZONE (Enthusiastic-Quiet)"
    # data for Enthusiastic-Quiet
    data_sheet['E53'] = '=COUNTIF(Table1[Enthusiastic],"=IN-PREF")'
    data_sheet['E54'] = '=COUNTIF(Table1[Quiet],"=IN-PREF")'
    data_sheet['E55'] = '=COUNTIF(Table1[Enthusiastic],"=OUT-OF-PREF")'
    data_sheet['E56'] = '=COUNTIF(Table1[Quiet],"=OUT-OF-PREF")'
    data_sheet['E57'] = '=COUNTIF(Table1[Quiet],"=MIDZONE")'

    # titles Concrete-Abstract
    data_sheet['D60'] = "Concrete-Abstract"
    data_sheet['D60'].font = Font(bold=True)
    data_sheet['D61'] = "In preference (Concrete)"
    data_sheet['D62'] = "In preference (Abstract)"
    data_sheet['D63'] = "Out of preference (Concrete)"
    data_sheet['D64'] = "Out of preference (Abstract)"
    data_sheet['D65'] = "MIDZONE (Concrete-Abstract)"
    # data for Concrete-Abstract
    data_sheet['E61'] = '=COUNTIF(Table1[Concrete],"=IN-PREF")'
    data_sheet['E62'] = '=COUNTIF(Table1[Abstract],"=IN-PREF")'
    data_sheet['E63'] = '=COUNTIF(Table1[Concrete],"=OUT-OF-PREF")'
    data_sheet['E64'] = '=COUNTIF(Table1[Abstract],"=OUT-OF-PREF")'
    data_sheet['E65'] = '=COUNTIF(Table1[Abstract],"=MIDZONE")'

    # titles Realistic-Imaginative
    data_sheet['D68'] = "Realistic-Imaginative"
    data_sheet['D68'].font = Font(bold=True)
    data_sheet['D69'] = "In preference (Realistic)"
    data_sheet['D70'] = "In preference (Imaginative)"
    data_sheet['D71'] = "Out of preference (Realistic)"
    data_sheet['D72'] = "Out of preference (Imaginative)"
    data_sheet['D73'] = "MIDZONE (Realistic-Imaginative)"
    # data for Realistic-Imaginative
    data_sheet['E69'] = '=COUNTIF(Table1[Realistic],"=IN-PREF")'
    data_sheet['E70'] = '=COUNTIF(Table1[Imaginative],"=IN-PREF")'
    data_sheet['E71'] = '=COUNTIF(Table1[Realistic],"=OUT-OF-PREF")'
    data_sheet['E72'] = '=COUNTIF(Table1[Imaginative],"=OUT-OF-PREF")'
    data_sheet['E73'] = '=COUNTIF(Table1[Imaginative],"=MIDZONE")'

    # titles Practical-Conceptual
    data_sheet['D76'] = "Practical-Conceptual"
    data_sheet['D76'].font = Font(bold=True)
    data_sheet['D77'] = "In preference (Practical)"
    data_sheet['D78'] = "In preference (Conceptual)"
    data_sheet['D79'] = "Out of preference (Practical)"
    data_sheet['D80'] = "Out of preference (Conceptual)"
    data_sheet['D81'] = "MIDZONE (Practical-Conceptual)"
    # data for Practical-Conceptual
    data_sheet['E77'] = '=COUNTIF(Table1[Practical],"=IN-PREF")'
    data_sheet['E78'] = '=COUNTIF(Table1[Conceptual],"=IN-PREF")'
    data_sheet['E79'] = '=COUNTIF(Table1[Practical],"=OUT-OF-PREF")'
    data_sheet['E80'] = '=COUNTIF(Table1[Conceptual],"=OUT-OF-PREF")'
    data_sheet['E81'] = '=COUNTIF(Table1[Conceptual],"=MIDZONE")'

    # titles Experiential-Theoretical
    data_sheet['D84'] = "Experiential-Theoretical"
    data_sheet['D84'].font = Font(bold=True)
    data_sheet['D85'] = "In preference (Experiential)"
    data_sheet['D86'] = "In preference (Theoretical)"
    data_sheet['D87'] = "Out of preference (Experiential)"
    data_sheet['D88'] = "Out of preference (Theoretical)"
    data_sheet['D89'] = "MIDZONE (Experiential-Theoretical)"
    # data for Experiential-Theoretical
    data_sheet['E85'] = '=COUNTIF(Table1[Experiential],"=IN-PREF")'
    data_sheet['E86'] = '=COUNTIF(Table1[Theoretical],"=IN-PREF")'
    data_sheet['E87'] = '=COUNTIF(Table1[Experiential],"=OUT-OF-PREF")'
    data_sheet['E88'] = '=COUNTIF(Table1[Theoretical],"=OUT-OF-PREF")'
    data_sheet['E89'] = '=COUNTIF(Table1[Theoretical],"=MIDZONE")'

    # titles Traditional-Original
    data_sheet['D92'] = "Traditional-Original"
    data_sheet['D92'].font = Font(bold=True)
    data_sheet['D93'] = "In preference (Traditional)"
    data_sheet['D94'] = "In preference (Original)"
    data_sheet['D95'] = "Out of preference (Traditional)"
    data_sheet['D96'] = "Out of preference (Original)"
    data_sheet['D97'] = "MIDZONE (Traditional-Original)"
    # data for Traditional-Original
    data_sheet['E93'] = '=COUNTIF(Table1[Traditional],"=IN-PREF")'
    data_sheet['E94'] = '=COUNTIF(Table1[Original],"=IN-PREF")'
    data_sheet['E95'] = '=COUNTIF(Table1[Traditional],"=OUT-OF-PREF")'
    data_sheet['E96'] = '=COUNTIF(Table1[Original],"=OUT-OF-PREF")'
    data_sheet['E97'] = '=COUNTIF(Table1[Original],"=MIDZONE")'

    # titles Logical-Empathetic
    data_sheet['D100'] = "Logical-Empathetic"
    data_sheet['D100'].font = Font(bold=True)
    data_sheet['D101'] = "In preference (Logical)"
    data_sheet['D102'] = "In preference (Empathetic)"
    data_sheet['D103'] = "Out of preference (Logical)"
    data_sheet['D104'] = "Out of preference (Empathetic)"
    data_sheet['D105'] = "MIDZONE (Logical-Empathetic)"
    # data for Logical-Empathetic
    data_sheet['E101'] = '=COUNTIF(Table1[Logical],"=IN-PREF")'
    data_sheet['E102'] = '=COUNTIF(Table1[Empathetic],"=IN-PREF")'
    data_sheet['E103'] = '=COUNTIF(Table1[Logical],"=OUT-OF-PREF")'
    data_sheet['E104'] = '=COUNTIF(Table1[Empathetic],"=OUT-OF-PREF")'
    data_sheet['E105'] = '=COUNTIF(Table1[Empathetic],"=MIDZONE")'

    # titles Reasonable-Compassionate
    data_sheet['D108'] = "Reasonable-Compassionate"
    data_sheet['D108'].font = Font(bold=True)
    data_sheet['D109'] = "In preference (Reasonable)"
    data_sheet['D110'] = "In preference (Compassionate)"
    data_sheet['D111'] = "Out of preference (Reasonable)"
    data_sheet['D112'] = "Out of preference (Compassionate)"
    data_sheet['D113'] = "MIDZONE (Reasonable-Compassionate)"
    # data for Reasonable-Compassionate
    data_sheet['E109'] = '=COUNTIF(Table1[Reasonable],"=IN-PREF")'
    data_sheet['E110'] = '=COUNTIF(Table1[Compassionate],"=IN-PREF")'
    data_sheet['E111'] = '=COUNTIF(Table1[Reasonable],"=OUT-OF-PREF")'
    data_sheet['E112'] = '=COUNTIF(Table1[Compassionate],"=OUT-OF-PREF")'
    data_sheet['E113'] = '=COUNTIF(Table1[Compassionate],"=MIDZONE")'

    # titles Questioning-Accommodating
    data_sheet['D116'] = "Questioning-Accommodating"
    data_sheet['D116'].font = Font(bold=True)
    data_sheet['D117'] = "In preference (Questioning)"
    data_sheet['D118'] = "In preference (Accommodating)"
    data_sheet['D119'] = "Out of preference (Questioning)"
    data_sheet['D120'] = "Out of preference (Accommodating)"
    data_sheet['D121'] = "MIDZONE (Questioning-Accommodating)"
    # data for Questioning-Accommodating
    data_sheet['E117'] = '=COUNTIF(Table1[Questioning],"=IN-PREF")'
    data_sheet['E118'] = '=COUNTIF(Table1[Accommodating],"=IN-PREF")'
    data_sheet['E119'] = '=COUNTIF(Table1[Questioning],"=OUT-OF-PREF")'
    data_sheet['E120'] = '=COUNTIF(Table1[Accommodating],"=OUT-OF-PREF")'
    data_sheet['E121'] = '=COUNTIF(Table1[Accommodating],"=MIDZONE")'

    # titles Critical-Accepting
    data_sheet['D124'] = "Critical-Accepting"
    data_sheet['D124'].font = Font(bold=True)
    data_sheet['D125'] = "In preference (Critical)"
    data_sheet['D126'] = "In preference (Accepting)"
    data_sheet['D127'] = "Out of preference (Critical)"
    data_sheet['D128'] = "Out of preference (Accepting)"
    data_sheet['D129'] = "MIDZONE (Critical-Accepting)"
    # data for Critical-Accepting
    data_sheet['E125'] = '=COUNTIF(Table1[Critical],"=IN-PREF")'
    data_sheet['E126'] = '=COUNTIF(Table1[Accepting],"=IN-PREF")'
    data_sheet['E127'] = '=COUNTIF(Table1[Critical],"=OUT-OF-PREF")'
    data_sheet['E128'] = '=COUNTIF(Table1[Accepting],"=OUT-OF-PREF")'
    data_sheet['E129'] = '=COUNTIF(Table1[Accepting],"=MIDZONE")'

    # titles Tough-Tender
    data_sheet['D132'] = "Tough-Tender"
    data_sheet['D132'].font = Font(bold=True)
    data_sheet['D133'] = "In preference (Tough)"
    data_sheet['D134'] = "In preference (Tender)"
    data_sheet['D135'] = "Out of preference (Tough)"
    data_sheet['D136'] = "Out of preference (Tender)"
    data_sheet['D137'] = "MIDZONE (Tough-Tender)"
    # data for Tough-Tender
    data_sheet['E133'] = '=COUNTIF(Table1[Tough],"=IN-PREF")'
    data_sheet['E134'] = '=COUNTIF(Table1[Tender],"=IN-PREF")'
    data_sheet['E135'] = '=COUNTIF(Table1[Tough],"=OUT-OF-PREF")'
    data_sheet['E136'] = '=COUNTIF(Table1[Tender],"=OUT-OF-PREF")'
    data_sheet['E137'] = '=COUNTIF(Table1[Tender],"=MIDZONE")'

    # titles Systematic-Casual
    data_sheet['D140'] = "Systematic-Casual"
    data_sheet['D140'].font = Font(bold=True)
    data_sheet['D141'] = "In preference (Systematic)"
    data_sheet['D142'] = "In preference (Casual)"
    data_sheet['D143'] = "Out of preference (Systematic)"
    data_sheet['D144'] = "Out of preference (Casual)"
    data_sheet['D145'] = "MIDZONE (Systematic-Casual)"
    # data for Systematic-Casual
    data_sheet['E141'] = '=COUNTIF(Table1[Systematic],"=IN-PREF")'
    data_sheet['E142'] = '=COUNTIF(Table1[Casual],"=IN-PREF")'
    data_sheet['E143'] = '=COUNTIF(Table1[Systematic],"=OUT-OF-PREF")'
    data_sheet['E144'] = '=COUNTIF(Table1[Casual],"=OUT-OF-PREF")'
    data_sheet['E145'] = '=COUNTIF(Table1[Casual],"=MIDZONE")'

    # titles Planful-Open-Ended
    data_sheet['D148'] = "Planful-Open-Ended"
    data_sheet['D148'].font = Font(bold=True)
    data_sheet['D149'] = "In preference (Planful)"
    data_sheet['D150'] = "In preference (Open-Ended)"
    data_sheet['D151'] = "Out of preference (Planful)"
    data_sheet['D152'] = "Out of preference (Open-Ended)"
    data_sheet['D153'] = "MIDZONE (Planful-Open-Ended)"
    # data for Planful-Open-Ended
    data_sheet['E149'] = '=COUNTIF(Table1[Planful],"=IN-PREF")'
    data_sheet['E150'] = '=COUNTIF(Table1[Open-Ended],"=IN-PREF")'
    data_sheet['E151'] = '=COUNTIF(Table1[Planful],"=OUT-OF-PREF")'
    data_sheet['E152'] = '=COUNTIF(Table1[Open-Ended],"=OUT-OF-PREF")'
    data_sheet['E153'] = '=COUNTIF(Table1[Open-Ended],"=MIDZONE")'

    # titles Early Starting-Pressure-Prompted
    data_sheet['D156'] = "Early Starting-Pressure-Prompted"
    data_sheet['D156'].font = Font(bold=True)
    data_sheet['D157'] = "In preference (Early Starting)"
    data_sheet['D158'] = "In preference (Pressure-Prompted)"
    data_sheet['D159'] = "Out of preference (Early Starting)"
    data_sheet['D160'] = "Out of preference (Pressure-Prompted)"
    data_sheet['D161'] = "MIDZONE (Early Starting-Pressure-Prompted)"
    # data for Early Starting-Pressure-Prompted
    data_sheet['E157'] = '=COUNTIF(Table1[Early Starting],"=IN-PREF")'
    data_sheet['E158'] = '=COUNTIF(Table1[Pressure-Prompted],"=IN-PREF")'
    data_sheet['E159'] = '=COUNTIF(Table1[Early Starting],"=OUT-OF-PREF")'
    data_sheet['E160'] = '=COUNTIF(Table1[Pressure-Prompted],"=OUT-OF-PREF")'
    data_sheet['E161'] = '=COUNTIF(Table1[Early Starting],"=MIDZONE")'

    # titles Scheduled-Spontaneous
    data_sheet['D164'] = "Scheduled-Spontaneous"
    data_sheet['D164'].font = Font(bold=True)
    data_sheet['D165'] = "In preference (Scheduled)"
    data_sheet['D166'] = "In preference (Spontaneous)"
    data_sheet['D167'] = "Out of preference (Scheduled)"
    data_sheet['D168'] = "Out of preference (Spontaneous)"
    data_sheet['D169'] = "MIDZONE (Scheduled-Spontaneous)"
    # data for Scheduled-Spontaneous
    data_sheet['E165'] = '=COUNTIF(Table1[Scheduled],"=IN-PREF")'
    data_sheet['E166'] = '=COUNTIF(Table1[Spontaneous],"=IN-PREF")'
    data_sheet['E167'] = '=COUNTIF(Table1[Scheduled],"=OUT-OF-PREF")'
    data_sheet['E168'] = '=COUNTIF(Table1[Spontaneous],"=OUT-OF-PREF")'
    data_sheet['E169'] = '=COUNTIF(Table1[Spontaneous],"=MIDZONE")'

    # titles Methodical-Emergent
    data_sheet['D172'] = "Methodical-Emergent"
    data_sheet['D172'].font = Font(bold=True)
    data_sheet['D173'] = "In preference (Methodical)"
    data_sheet['D174'] = "In preference (Emergent)"
    data_sheet['D175'] = "Out of preference (Methodical)"
    data_sheet['D176'] = "Out of preference (Emergent)"
    data_sheet['D177'] = "MIDZONE (Methodical-Emergent)"
    # data for Methodical-Emergent
    data_sheet['E173'] = '=COUNTIF(Table1[Methodical],"=IN-PREF")'
    data_sheet['E174'] = '=COUNTIF(Table1[Emergent],"=IN-PREF")'
    data_sheet['E175'] = '=COUNTIF(Table1[Methodical],"=OUT-OF-PREF")'
    data_sheet['E176'] = '=COUNTIF(Table1[Emergent],"=OUT-OF-PREF")'
    data_sheet['E177'] = '=COUNTIF(Table1[Emergent],"=MIDZONE")'


def prepare_facet_legend(chart_sheet):
    # add white text rule to the black background for text readability

    # add text
    chart_sheet['V30'] = "Facets Legend"
    chart_sheet['V30'].font = Font(bold=True)

    chart_sheet['X31'] = "1ST facet - In-Preference"
    chart_sheet['X32'] = "2ND facet - In-Preference"
    chart_sheet['X33'] = "1ST facet - Out-of-Preference"
    chart_sheet['X34'] = "2ND facet - Out-of-Preference"
    chart_sheet['X35'] = "MIDZONE"



def prepare_external_internal_data(data_sheet):
    Internal_list = ["ST", "SF", "NF", "NT"]
    External_list = ["IJ", "IP", "EJ", "EP"]

    data_sheet['G1'] = "Internal Analysis"
    data_sheet['J1'] = "External Analysis"
    data_sheet['G1'].font = Font(bold=True)
    data_sheet['J1'].font = Font(bold=True)
    data_sheet['G2'] = "Internal"
    data_sheet['J2'] = "External"
    data_sheet['H2'] = "Count"
    data_sheet['K2'] = "Count"
    data_sheet['H3'] = '=COUNTIF(Table1[Type], "*ST*")'
    data_sheet['H4'] = '=COUNTIF(Table1[Type], "*SF*")'
    data_sheet['H5'] = '=COUNTIF(Table1[Type], "*NF*")'
    data_sheet['H6'] = '=COUNTIF(Table1[Type], "*NT*")'
    data_sheet['K3'] = '=COUNTIF(Table1[Type], "I*J")'
    data_sheet['K4'] = '=COUNTIF(Table1[Type], "I*P")'
    data_sheet['K5'] = '=COUNTIF(Table1[Type], "E*J")'
    data_sheet['K6'] = '=COUNTIF(Table1[Type], "E*P")'

    # Insert Internal_list at G3->G6
    for i, internal_type in enumerate(Internal_list):
        data_sheet[f'G{3 + i}'] = internal_type

    # Insert External_list at J3->J6
    for i, external_type in enumerate(External_list):
        data_sheet[f'J{3 + i}'] = external_type


def prepare_dominant_function_data(data_sheet):


    data_sheet['G9'] = "Dominant Function Data"
    data_sheet['G9'].font = Font(bold=True)
    data_sheet['G10'] = "Dominant Function"
    data_sheet['H10'] = "Count"
    data_sheet['G11'] = "Te"
    data_sheet['H11'] = '=SUM(B17,B14)'
    data_sheet['G12'] = "Ti"
    data_sheet['H12'] = '=SUM(B9,B6)'
    data_sheet['G13'] = "Ne"
    data_sheet['H13'] = '=SUM(B12,B13)'
    data_sheet['G14'] = "Ni"
    data_sheet['H14'] = '=SUM(B4,B5)'
    data_sheet['G15'] = "Fe"
    data_sheet['H15'] = '=SUM(B16,B15)'
    data_sheet['G16'] = "Fi"
    data_sheet['H16'] = '=SUM(B8,B7)'
    data_sheet['G17'] = "Se"
    data_sheet['H17'] = '=SUM(B11,B10)'
    data_sheet['G18'] = "Si"
    data_sheet['H18'] = '=SUM(B3,B2)'


def create_main_distribution_chart(data_sheet, chart_sheet):
    # Create pie chart
    main_chart = PieChart()
    main_chart.title = "Distribution by Type"

    # Set data references
    labels = Reference(data_sheet, min_col=1, min_row=2, max_row=17)
    data = Reference(data_sheet, min_col=2, min_row=2, max_row=17)

    # Add data to chart
    main_chart.add_data(data)
    main_chart.set_categories(labels)
    main_chart.legend = None

    # Chart size
    main_chart.width = 11.8618
    main_chart.height = 13.1826

    # Data labels
    main_chart.dataLabels = DataLabelList()
    main_chart.dataLabels.showCatName = True
    main_chart.dataLabels.showPercent = True
    main_chart.dataLabels.showVal = False
    main_chart.dataLabels.showSerName = False

    # Add the chart to the sheet
    chart_sheet.add_chart(main_chart, "C3")

    return main_chart


def create_dichotomy_charts(data_sheet, chart_sheet):
    # Create stacked bar charts for each dichotomy
    create_stacked_dichotomy_chart(data_sheet, chart_sheet, "Energy source - E/I", 3, 4, "K3")
    create_stacked_dichotomy_chart(data_sheet, chart_sheet, "Information - S/N", 7, 8, "V3")
    create_stacked_dichotomy_chart(data_sheet, chart_sheet, "Decisions - T/F", 11, 12, "K16")
    create_stacked_dichotomy_chart(data_sheet, chart_sheet, "Lifestyle - J/P", 15, 16, "V16")


def create_stacked_dichotomy_chart(data_sheet, chart_sheet, title, label_row, count_row, position):
    # Create a horizontal stacked bar chart
    chart = BarChart()
    chart.type = "bar"
    chart.title = title
    chart.style = 10

    # Set chart size
    chart.width = 16.9164
    chart.height = 2.69

    # Reference the count data
    data = Reference(data_sheet, min_col=4, max_col=5, min_row=count_row, max_row=count_row)

    # Reference the labels
    cats = Reference(data_sheet, min_col=4, max_col=5, min_row=label_row, max_row=label_row)

    # Add data and categories
    chart.add_data(data, titles_from_data=False)
    chart.set_categories(cats)

    # Configure chart appearance
    chart.y_axis.delete = True  # Remove y-axis
    chart.plot_area.dTable = None
    chart.x_axis.majorGridlines = None
    chart.x_axis.minorGridlines = None
    chart.legend = None

    # Make it stacked
    chart.grouping = "percentStacked"
    chart.overlap = 100
    chart.x_axis.majorGridlines = None
    chart.x_axis.minorGridlines = None
    chart.y_axis.majorGridlines = None
    chart.y_axis.minorGridlines = None
    # Remove vertical lines by setting the x-axis line properties to None
    chart.x_axis.spPr = GraphicalProperties()
    chart.x_axis.spPr.ln = LineProperties(noFill=True)
    # Remove tick marks
    chart.x_axis.majorTickMark = "none"
    chart.x_axis.minorTickMark = "none"
    # Hide legend
    chart.legend = None
    # Add data labels
    chart.dataLabels = DataLabelList()
    chart.dataLabels.showPercent = True
    chart.dataLabels.showVal = False
    chart.dataLabels.showCatName = True
    chart.dataLabels.showSerName = False
    chart.dataLabels.position = "ctr"
    # Format the percentage display
    chart.dataLabels.numFmt = '0%'

    # Add legend back and position it below the title
    chart.legend = None  # First remove any existing legend
    chart.legend = openpyxl.chart.legend.Legend()
    chart.legend.position = 't'
    chart.legend.topMode = None
    chart.legend.overlay = False
    manual = ManualLayout(
        x=0.33,      # Center horizontally (0.5 = 50%)
        y=0.15,     # Position vertically (adjust as needed)
        h=0.05,     # Height (adjust as needed)
        w=0.9       # Width (adjust as needed)
    )
    chart.legend.layout = Layout(manualLayout=manual)
    chart.legend.horAlign = 'center'
    left_label = data_sheet.cell(row=label_row, column=4).value
    right_label = data_sheet.cell(row=label_row, column=5).value
    # Add the chart to the sheet
    chart_sheet.add_chart(chart, position)
    # Initialize series titles if needed
    for i, s in enumerate(chart.series):
        if i == 0:
            # Create a new text object if none exists
            if s.tx is None:
                s.tx = SeriesLabel(v=left_label)
            else:
                # Set the value directly
                s.tx.v = left_label
        elif i == 1:
            # Create a new text object if none exists
            if s.tx is None:
                s.tx = SeriesLabel(v=right_label)
            else:
                # Set the value directly
                s.tx.v = right_label
    return chart


def create_external_internal_charts(data_sheet, chart_sheet):
    # Create Internal Analysis Pie Chart
    internal_pie = PieChart()
    internal_pie.title = "Internal Analysis Distribution"
    labels = Reference(data_sheet, min_col=7, min_row=3, max_row=6)
    data = Reference(data_sheet, min_col=8, min_row=3, max_row=6)
    internal_pie.add_data(data, titles_from_data=False)
    internal_pie.set_categories(labels)
    internal_pie.width = 8.43
    internal_pie.height = 8.128

    # Create External Analysis Pie Chart
    external_pie = PieChart()
    external_pie.title = "External Analysis Distribution"
    labels = Reference(data_sheet, min_col=10, min_row=3, max_row=6)
    data = Reference(data_sheet, min_col=11, min_row=3, max_row=6)
    external_pie.add_data(data, titles_from_data=False)
    external_pie.set_categories(labels)
    external_pie.width = 8.43
    external_pie.height = 8.128

    # Configure data labels for both charts
    for pie in [internal_pie, external_pie]:
        pie.dataLabels = DataLabelList()
        pie.dataLabels.showCatName = False
        pie.dataLabels.showVal = False
        pie.dataLabels.showPercent = True
        pie.dataLabels.showSerName = False

    # Add the charts to the sheet
    chart_sheet.add_chart(internal_pie, "K30")
    chart_sheet.add_chart(external_pie, "P30")


def create_dominant_chart(data_sheet, chart_sheet):
    dominant_pie = PieChart()
    dominant_pie.title = "Dominant Function"
    labels = Reference(data_sheet, min_col=7, min_row=11, max_row=18)
    data = Reference(data_sheet, min_col=8, min_row=11, max_row=18)
    dominant_pie.add_data(data, titles_from_data=False)
    dominant_pie.set_categories(labels)
    dominant_pie.width = 11.8618
    dominant_pie.height = 8.128
    # Configure data labels for dominant function chart
    dominant_pie.dataLabels = DataLabelList()
    dominant_pie.dataLabels.showCatName = True
    dominant_pie.dataLabels.showVal = False
    dominant_pie.dataLabels.showPercent = True
    dominant_pie.dataLabels.showSerName = False

    # Add the chart to the sheet
    chart_sheet.add_chart(dominant_pie, "C30")


def create_facet_bar_charts(data_sheet, chart_sheet):
    # Create pie charts for facet dichotomies, organized in rows

    # Row 1: E/I facets
    create_facet_pie_chart(data_sheet, chart_sheet, "D20", "D21:D25", "E21:E25", "K9")  # Initiating-Receiving
    create_facet_pie_chart(data_sheet, chart_sheet, "D28", "D29:D33", "E29:E33", "M9")  # Expressive-Contained
    create_facet_pie_chart(data_sheet, chart_sheet, "D36", "D37:D41", "E37:E41", "O9")  # Gregarious-Intimate
    create_facet_pie_chart(data_sheet, chart_sheet, "D44", "D45:D49", "E45:E49", "Q9")  # Active-Reflective
    create_facet_pie_chart(data_sheet, chart_sheet, "D52", "D53:D57", "E53:E57", "S9")  # Enthusiastic-Quiet

    # Row 2: S/N facets
    create_facet_pie_chart(data_sheet, chart_sheet, "D60", "D61:D65", "E61:E65", "V9")  # Concrete-Abstract
    create_facet_pie_chart(data_sheet, chart_sheet, "D68", "D69:D73", "E69:E73", "X9")  # Realistic-Imaginative
    create_facet_pie_chart(data_sheet, chart_sheet, "D76", "D77:D81", "E77:E81", "Z9")  # Practical-Conceptual
    create_facet_pie_chart(data_sheet, chart_sheet, "D84", "D85:D89", "E85:E89", "AB9")  # Experiential-Theoretical
    create_facet_pie_chart(data_sheet, chart_sheet, "D92", "D93:D97", "E93:E97", "AD9")  # Traditional-Original

    # Row 3: T/F facets
    create_facet_pie_chart(data_sheet, chart_sheet, "D100", "D101:D105", "E101:E105", "K22")  # Logical-Empathetic
    create_facet_pie_chart(data_sheet, chart_sheet, "D108", "D109:D113", "E109:E113", "M22")  # Reasonable-Compassionate
    create_facet_pie_chart(data_sheet, chart_sheet, "D116", "D117:D121", "E117:E121", "O22")  # Questioning-Accommodating
    create_facet_pie_chart(data_sheet, chart_sheet, "D124", "D125:D129", "E125:E129", "Q22")  # Critical-Accepting
    create_facet_pie_chart(data_sheet, chart_sheet, "D132", "D133:D137", "E133:E137", "S22")  # Tough-Tender

    # Row 4: J/P facets
    create_facet_pie_chart(data_sheet, chart_sheet, "D140", "D141:D145", "E141:E145", "V22")  # Systematic-Casual
    create_facet_pie_chart(data_sheet, chart_sheet, "D148", "D149:D153", "E149:E153", "X22")  # Planful-Open-Ended
    create_facet_pie_chart(data_sheet, chart_sheet, "D156", "D157:D161", "E157:E161", "Z22")  # Early Starting-Pressure-Prompted
    create_facet_pie_chart(data_sheet, chart_sheet, "D164", "D165:D169", "E165:E169", "AB22")  # Scheduled-Spontaneous
    create_facet_pie_chart(data_sheet, chart_sheet, "D172", "D173:D177", "E173:E177", "AD22")  # Methodical-Emergent


def create_facet_pie_chart(data_sheet, chart_sheet, title_cell, labels_range, data_range, position):
    """Create a stacked bar chart for a facet dichotomy with improved styling"""
    # Create a horizontal stacked bar chart
    chart = BarChart()
    chart.type = "bar"
    # Get the title from the specified cell
    title = data_sheet[title_cell].value
    chart.title = title
    chart.style = 10
    # Set chart size
    chart.width = 3.2766
    chart.height = 3.5
    # Reference the data and labels
    data = Reference(data_sheet, range_string=f"Data!{data_range}")
    labels = Reference(data_sheet, range_string=f"Data!{labels_range}")
    # Add data and categories
    chart.add_data(data, from_rows=True)
    chart.set_categories(labels)
    # Configure chart appearance
    chart.y_axis.delete = True  # Remove y-axis
    chart.plot_area.dTable = None
    chart.x_axis.majorGridlines = None
    chart.x_axis.minorGridlines = None
    # Make it stacked
    chart.grouping = "percentStacked"
    chart.overlap = 100
    chart.y_axis.majorGridlines = None
    chart.y_axis.minorGridlines = None
    # Remove vertical lines by setting the x-axis line properties to None
    chart.x_axis.spPr = GraphicalProperties()
    chart.x_axis.spPr.ln = LineProperties(noFill=True)
    # Remove tick marks
    chart.x_axis.majorTickMark = "none"
    chart.x_axis.minorTickMark = "none"
    # Add data labels
    chart.dataLabels = DataLabelList()
    chart.dataLabels.showPercent = False
    chart.dataLabels.showVal = False
    chart.dataLabels.showCatName = False
    chart.dataLabels.showSerName = False
    chart.dataLabels.position = "ctr"
    # Format the percentage display
    chart.dataLabels.numFmt = '0%'
    # Set legend position to bottom
    chart.legend = None
    # chart.legend.position = 'b'
    # Add the chart to the sheet
    chart_sheet.add_chart(chart, position)
    return chart


def adjust_column_widths(sheet):
    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        sheet.column_dimensions[column_letter].width = adjusted_width


def reorder_sheets(workbook):
    """
    Reorders the sheets in the workbook to a logical order:
    1. Main data sheet (MBTI Results)
    2. Charts/Dashboard
    3. Section sheets
    4. Any other sheets
    """
    # Define the preferred order
    preferred_order = ["Dashboard", "MBTI Results", "Charts"]

    # Get current sheet names
    current_sheets = workbook.sheetnames

    # Create a new order list
    new_order = []

    # First add sheets from preferred order if they exist
    for sheet_name in preferred_order:
        if sheet_name in current_sheets:
            new_order.append(sheet_name)
            current_sheets.remove(sheet_name)

    # Then add any section sheets (they typically start with "Section")
    section_sheets = [name for name in current_sheets if name.startswith("Section")]
    section_sheets.sort()  # Sort section sheets numerically if possible
    new_order.extend(section_sheets)
    for name in section_sheets:
        current_sheets.remove(name)

    # Add any remaining sheets
    new_order.extend(current_sheets)

    # Reorder the sheets
    for i, sheet_name in enumerate(new_order):
        sheet = workbook[sheet_name]
        workbook.move_sheet(sheet, i)

    print(f"Sheets reordered to: {new_order}")
    return workbook


def reset_column_widths(chart_sheet):
    """Reset all column widths to default before applying specific widths"""
    # Standard default column width in Excel
    default_width = 8.43  # This is Excel's default column width

    # Reset all columns to default width
    for col_idx in range(1, 100):  # Adjust range as needed based on your dashboard width
        col_letter = openpyxl.utils.get_column_letter(col_idx)
        chart_sheet.column_dimensions[col_letter].width = default_width


if __name__ == "__main__":
    # For testing purposes
    import openpyxl

    workbook_path = r"F:\projects\MBTInfo\output\MBTI_Results.xlsx"
    workbook = openpyxl.load_workbook(workbook_path)
    create_distribution_charts(workbook)
    workbook.save(workbook_path)