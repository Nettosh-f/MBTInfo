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
    "Initiating", "Receiving",
    "Expressive", "Contained",
    "Gregarious", "Intimate",
    "Active", "Reflective",
    "Enthusiastic", "Quiet",
    "Concrete", "Abstract",
    "Realistic", "Imaginative",
    "Practical", "Conceptual",
    "Experiential", "Theoretical",
    "Traditional", "Original",
    "Logical", "Empathetic",
    "Reasonable", "Compassionate",
    "Questioning", "Accommodating",
    "Critical", "Accepting",
    "Tough", "Tender",
    "Systematic", "Casual",
    "Planful", "Open-Ended",
    "Early Starting", "Pressure-Prompted",
    "Scheduled", "Spontaneous",
    "Methodical", "Emergent"
]

MIDZONE_FACETS = [
    "Initiating–Receiving", "Expressive–Contained", "Gregarious–Intimate",
    "Active–Reflective", "Enthusiastic–Quiet", "Concrete–Abstract",
    "Realistic–Imaginative", "Practical–Conceptual", "Experiential–Theoretical",
    "Traditional–Original", "Logical–Empathetic", "Reasonable–Compassionate",
    "Questioning–Accommodating", "Critical–Accepting", "Tough–Tender",
    "Systematic–Casual", "Planful–Open-Ended", "Early Starting–Pressure-Prompted",
    "Scheduled–Spontaneous", "Methodical–Emergent"
]

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

type_descriptions = {
    'ISTJ': 'Quiet, serious, thorough, dependable, practical, matter-of-fact, realistic, and responsible.',
    'ISFJ': 'Quiet, friendly, responsible, conscientious, committed, steady, and detail-oriented.',
    'INFJ': 'Seek meaning and connection, insightful about others, organized, decisive, values-driven.',
    'INTJ': 'Original, driven by their own ideas and purpose, skeptical, independent, high standards.',
    'ISTP': 'Tolerant, flexible, observant, practical problem-solvers, logical, and analytical.',
    'ISFP': 'Quiet, friendly, sensitive, kind, present-oriented, enjoy their own space.',
    'INFP': 'Idealistic, loyal to values, curious, seek to understand people, adaptable, flexible.',
    'INTP': 'Seek logical explanations, theoretical, abstract, more interested in ideas than social interaction.',
    'ESTP': 'Flexible, tolerant, pragmatic, focused on immediate results, energetic, and spontaneous.',
    'ESFP': 'Outgoing, friendly, accepting, enjoy working with others, realistic, spontaneous.',
    'ENFP': 'Enthusiastic, imaginative, see possibilities, spontaneous, flexible, innovative.',
    'ENTP': 'Quick, ingenious, stimulating, alert, outspoken, resourceful, and adaptable.',
    'ESTJ': 'Practical, realistic, matter-of-fact, decisive, focus on efficient results.',
    'ESFJ': 'Warmhearted, conscientious, cooperative, seek harmony, work with determination.',
    'ENFJ': 'Warm, empathetic, responsive, responsible, sociable, highly attuned to others.',
    'ENTJ': 'Frank, decisive, assume leadership readily, structured, logical, and efficient.'
}

career_insights = {
    'ISTJ': "You excel in roles requiring attention to detail, reliability, and logical organization. Consider careers in accounting, project management, logistics, or quality assurance.",
    'ISFJ': "You thrive in supportive roles where you can help others in practical ways. Consider careers in healthcare, education, administrative support, or social services.",
    'INFJ': "You're drawn to meaningful work that aligns with your values. Consider careers in counseling, writing, non-profit work, or human resources development.",
    'INTJ': "You excel in strategic planning and complex problem-solving. Consider careers in systems analysis, scientific research, strategic planning, or engineering.",
    'ISTP': "You enjoy hands-on problem-solving and technical challenges. Consider careers in mechanics, engineering, technical troubleshooting, or emergency response.",
    'ISFP': "You thrive in creative roles with practical applications. Consider careers in design, healthcare, culinary arts, or personal care services.",
    'INFP': "You're motivated by work that aligns with your personal values. Consider careers in writing, counseling, teaching, or artistic pursuits.",
    'INTP': "You excel in theoretical and analytical problem-solving. Consider careers in research, programming, systems analysis, or academia.",
    'ESTP': "You thrive in dynamic, action-oriented environments. Consider careers in sales, entrepreneurship, emergency services, or sports.",
    'ESFP': "You excel in people-oriented, practical roles. Consider careers in entertainment, sales, customer service, or event planning.",
    'ENFP': "You're drawn to creative work involving people and possibilities. Consider careers in counseling, teaching, marketing, or public relations.",
    'ENTP': "You thrive in innovative, intellectually stimulating environments. Consider careers in entrepreneurship, consulting, creative design, or technology.",
    'ESTJ': "You excel in structured leadership roles. Consider careers in management, administration, law enforcement, or military leadership.",
    'ESFJ': "You thrive in roles focused on supporting others' wellbeing. Consider careers in healthcare, education, customer service, or community services.",
    'ENFJ': "You're drawn to roles where you can inspire and develop others. Consider careers in teaching, counseling, human resources, or non-profit leadership.",
    'ENTJ': "You excel in strategic leadership and organizational development. Consider careers in executive leadership, consulting, law, or business development."
}