from pathlib import Path

MBTI_TYPES = [
    "ISTJ", "ISFJ", "INFJ", "INTJ",
    "ISTP", "ISFP", "INFP", "INTP",
    "ESTP", "ESFP", "ENFP", "ENTP",
    "ESTJ", "ESFJ", "ENFJ", "ENTJ"
]

MBTI_LETTERS = {
    "E": "Extroversion", "I": "Introversion", "S": "Sensing", "N": "Intuition", "T": "Thinking", "F": "Feeling",
    "J": "Judging", "P": "Perceiving"}

FACETS = [
    "Initiating", "Receiving", "Expressive", "Contained", "Gregarious", "Intimate", "Active", "Reflective", "Enthusiastic", "Quiet",
    "Concrete", "Abstract", "Realistic", "Imaginative", "Practical", "Conceptual", "Experiential", "Theoretical", "Traditional", "Original",
    "Logical", "Empathetic", "Reasonable", "Compassionate", "Questioning", "Accommodating", "Critical", "Accepting", "Tough", "Tender",
    "Systematic", "Casual", "Planful", "Open-Ended", "Early Starting", "Pressure-Prompted", "Scheduled", "Spontaneous", "Methodical", "Emergent"
]

MIDZONE_FACETS = [
    "Initiating–Receiving", "Expressive–Contained", "Gregarious–Intimate", "Active–Reflective", "Enthusiastic–Quiet",
    "Concrete–Abstract", "Realistic–Imaginative", "Practical–Conceptual", "Experiential–Theoretical", "Traditional–Original",
    "Logical–Empathetic", "Reasonable–Compassionate", "Questioning–Accommodating", "Critical–Accepting", "Tough–Tender",
    "Systematic–Casual", "Planful–Open-Ended", "Early Starting–Pressure-Prompted", "Scheduled–Spontaneous", "Methodical–Emergent"
]
All_Facets = FACETS + MIDZONE_FACETS

mbti_colors = {
    "ISTJ": "FFB3BA", "ISFJ": "BAFFC9", "INFJ": "BAE1FF", "INTJ": "FFDFBA",
    "ISTP": "FFFFBA", "ISFP": "FFB3FF", "INFP": "B3FFF9", "INTP": "FFB3B3",
    "ESTP": "C1B3FF", "ESFP": "B3FFB3", "ENFP": "FFC9B3", "ENTP": "B3BAFF",
    "ESTJ": "FFB3E6", "ESFJ": "B3FFE6", "ENFJ": "FFE1B3", "ENTJ": "B3E1FF"
}

facet_and_midzone_colors = {
    "Initiating": "#00FF00",
    "Receiving": "#FFA500",
    "Expressive": "#00BFFF",
    "Contained": "#000080",
    "Gregarious": "#2E8B57",
    "Intimate": "#8A2BE2",
    "Active": "#DA70D6",
    "Reflective": "#DC143C",
    "Enthusiastic": "#9ACD32",
    "Quiet": "#008080",
    "Concrete": "#FF4500",
    "Abstract": "#800000",
    "Realistic": "#FFD700",
    "Imaginative": "#20B2AA",
    "Practical": "#9932CC",
    "Conceptual": "#556B2F",
    "Experiential": "#FF6347",
    "Theoretical": "#8B4513",
    "Traditional": "#4682B4",
    "Original": "#B22222",
    "Logical": "#ADFF2F",
    "Empathetic": "#00CED1",
    "Reasonable": "#7B68EE",
    "Compassionate": "#FF69B4",
    "Questioning": "#1E90FF",
    "Accommodating": "#A52A2A",
    "Critical": "#6A5ACD",
    "Accepting": "#32CD32",
    "Tough": "#00FA9A",
    "Tender": "#BA55D3",
    "Systematic": "#7FFF00",
    "Casual": "#CD5C5C",
    "Planful": "#0000CD",
    "Open-Ended": "#F08080",
    "Early Starting": "#3CB371",
    "Pressure-Prompted": "#FF8C00",
    "Scheduled": "#00BFFF",
    "Spontaneous": "#9370DB",
    "Methodical": "#DAA520",
    "Emergent": "#40E0D0",

    "Initiating–Receiving": "#80D280",
    "Expressive–Contained": "#0040BF",
    "Gregarious–Intimate": "#5D5F8C",
    "Active–Reflective": "#EE41A1",
    "Enthusiastic–Quiet": "#4D9979",
    "Concrete–Abstract": "#BF2200",
    "Realistic–Imaginative": "#8DBD65",
    "Practical–Conceptual": "#748A77",
    "Experiential–Theoretical": "#D28A30",
    "Traditional–Original": "#80538B",
    "Logical–Empathetic": "#56E7AA",
    "Reasonable–Compassionate": "#C6B589",
    "Questioning–Accommodating": "#93A0BF",
    "Critical–Accepting": "#4C948E",
    "Tough–Tender": "#5ECDC3",
    "Systematic–Casual": "#97BF66",
    "Planful–Open-Ended": "#7E4684",
    "Early Starting–Pressure-Prompted": "#AFA556",
    "Scheduled–Spontaneous": "#4961B6",
    "Methodical–Emergent": "#A4C390"
}

dominant_type = {"ISTJ": "Si", "ISFJ": "Si", "INFJ": "Ni", "INTJ": "Ni", "ISTP": "Ti",
                 "ISFP": "Fi", "INFP": "Fi", "INTP": "Ti", "ESTP": "Se", "ESFP": "Se",
                 "ENFP": "Ne", "ENTP": "Ne", "ESTJ": "Te", "ESFJ": "Fe", "ENFJ": "Fe",
                 "ENTJ": "Te"}


dominant_functions = {
    "ENTJ": "Te",
    "ESTJ": "Te",
    "INTP": "Ti",
    "ISTP": "Ti",
    "ENFP": "Ne",
    "ENTP": "Ne",
    "INFJ": "Ni",
    "INTJ": "Ni",
    "ENFJ": "Fe",
    "ESFJ": "Fe",
    "INFP": "Fi",
    "ISFP": "Fi",
    "ESFP": "Se",
    "ESTP": "Se",
    "ISFJ": "Si",
    "ISTJ": "Si",
}

mbti_pair_explanations = {
    # External qualities (how we interact with the world)
    "EJ": "Decisive and structured in dealing with the external world, naturally taking charge of situations and implementing clear plans.",
    "EP": "Adaptable and spontaneous with the external world, preferring to keep options open and respond flexibly to new information.",
    "IJ": "Reflective and cautious about the external world, preferring to observe thoroughly before committing to definitive action.",
    "IP": "Independent and contemplative in approach, needing personal space to process information before engaging with the external environment.",

    # Internal qualities (how we process information)
    "ST": "Practical and factual in decision making, analyzing concrete data and applying logical reasoning to reach objective conclusions.",
    "SF": "Detail-oriented and empathetic, making decisions by considering practical needs while remaining sensitive to how choices affect people.",
    "NT": "Analytical and theoretical in thinking, focusing on systems, concepts, and logical frameworks rather than immediate practical applications.",
    "NF": "Idealistic and insight-driven, processing information through the lens of values, possibilities, and human potential.",

    # Additional combinations
    "TJ": "Structured and logical in approach, creating systems and frameworks to efficiently accomplish goals through objective reasoning.",
    "TP": "Analytical but flexible thinkers who examine problems from multiple angles while maintaining logical detachment.",
    "FJ": "Organized and people-focused, creating harmony through structured approaches to relationships and community needs.",
    "FP": "Compassionate and adaptable, valuing authentic expression and remaining open to the emotional needs of each unique situation."
}

facet_chart_list = {
    "page5_EIGraph.png": ["Initiating", "Receiving", "Expressive", "Contained", "Gregarious", "Intimate", "Active", "Reflective", "Enthusiastic", "Quiet", "Initiating–Receiving", "Expressive–Contained", "Gregarious–Intimate", "Active–Reflective", "Enthusiastic–Quiet"],
    "page6_SNgraph.png": ["Concrete", "Abstract", "Realistic", "Imaginative","Practical", "Conceptual","Experiential", "Theoretical","Traditional", "Original", "Concrete–Abstract", "Realistic–Imaginative", "Practical–Conceptual", "Experiential–Theoretical", "Traditional–Original"],
    "page7_TFgraph.png": ["Logical", "Empathetic", "Reasonable", "Compassionate", "Questioning", "Accommodating", "Critical", "Accepting", "Tough", "Tender",     "Logical–Empathetic", "Reasonable–Compassionate", "Questioning–Accommodating", "Critical–Accepting", "Tough–Tender"],
    "page8_JPgraph.png": ["Systematic", "Casual", "Planful", "Open-Ended", "Early Starting", "Pressure-Prompted", "Scheduled", "Spontaneous", "Methodical", "Emergent",     "Systematic–Casual", "Planful–Open-Ended", "Early Starting–Pressure-Prompted", "Scheduled–Spontaneous", "Methodical–Emergent"]
}

VALIDATION_SYSTEM_PROMPT = (
    "Determine whether the attached PDF is clearly related to MBTI (Myers-Briggs Type Indicator), "
    "personality types, or psychological typing. If it is, respond with YES. "
    "If not, respond with NO and explain briefly."
)

INSIGHT_SYSTEM_PROMPT = ("""
    You are a professional MBTI coach for businesses and individuals. 
    You give insight for professional growth based on the given PDF. 
    If the file is not MBTI-related, you must not answer.
    Here you are Given a pdf that summarizes a full MBTI report for an individual.
    your goal is to provide short insightful advice and strategies for the individual to improve their MBTI personality type.
    Structure your response as an HTML page with appropriate tags, titles, and styling.
    """)

INSIGHT_COUPLE_SYSTEM_PROMPT = ("""
    You are a professional MBTI coach for businesses and individuals. 
    You give insight for professional growth based on the given PDF. 
    Here you are Given a pdf that combines 2 personal reports for a comparison.
    give insight into healthy cooperation and trust, potential conflict points, 
    and potential solutions.
    Structure your response as an HTML page with appropriate tags, titles, and styling.
""")




PROJECT_BASE_DIR = Path(r"F:\projects\MBTInfo")
MEDIA_PATH = Path(r"F:\projects\MBTInfo\backend\media")
OUTPUT_PATH = Path(r"F:\projects\MBTInfo\output")
INPUT_PATH = Path(r"F:\projects\MBTInfo\input")

