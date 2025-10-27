import os
import tempfile
from pathlib import Path

MBTI_TYPES = [
    "ISTJ",
    "ISFJ",
    "INFJ",
    "INTJ",
    "ISTP",
    "ISFP",
    "INFP",
    "INTP",
    "ESTP",
    "ESFP",
    "ENFP",
    "ENTP",
    "ESTJ",
    "ESFJ",
    "ENFJ",
    "ENTJ",
]

MBTI_LETTERS = {
    "E": "Extroversion",
    "I": "Introversion",
    "S": "Sensing",
    "N": "Intuition",
    "T": "Thinking",
    "F": "Feeling",
    "J": "Judging",
    "P": "Perceiving",
}

DICHOTOMY_NAMES = [
    "Extroversion",
    "Introversion",
    "Sensing",
    "Intuition",
    "Thinking",
    "Feeling",
    "Judging",
    "Perceiving",
]

FACETS = [
    "Initiating",
    "Receiving",
    "Expressive",
    "Contained",
    "Gregarious",
    "Intimate",
    "Active",
    "Reflective",
    "Enthusiastic",
    "Quiet",
    "Concrete",
    "Abstract",
    "Realistic",
    "Imaginative",
    "Practical",
    "Conceptual",
    "Experiential",
    "Theoretical",
    "Traditional",
    "Original",
    "Logical",
    "Empathetic",
    "Reasonable",
    "Compassionate",
    "Questioning",
    "Accommodating",
    "Critical",
    "Accepting",
    "Tough",
    "Tender",
    "Systematic",
    "Casual",
    "Planful",
    "Open-Ended",
    "Early Starting",
    "Pressure-Prompted",
    "Scheduled",
    "Spontaneous",
    "Methodical",
    "Emergent",
]

MIDZONE_FACETS = [
    "Initiating–Receiving",
    "Expressive–Contained",
    "Gregarious–Intimate",
    "Active–Reflective",
    "Enthusiastic–Quiet",
    "Concrete–Abstract",
    "Realistic–Imaginative",
    "Practical–Conceptual",
    "Experiential–Theoretical",
    "Traditional–Original",
    "Logical–Empathetic",
    "Reasonable–Compassionate",
    "Questioning–Accommodating",
    "Critical–Accepting",
    "Tough–Tender",
    "Systematic–Casual",
    "Planful–Open-Ended",
    "Early Starting–Pressure-Prompted",
    "Scheduled–Spontaneous",
    "Methodical–Emergent",
]
ALL_FACETS = FACETS + MIDZONE_FACETS

MBTI_COLORS = {
    "ISTJ": "FFB3BA",
    "ISFJ": "BAFFC9",
    "INFJ": "BAE1FF",
    "INTJ": "FFDFBA",
    "ISTP": "FFFFBA",
    "ISFP": "FFB3FF",
    "INFP": "B3FFF9",
    "INTP": "FFB3B3",
    "ESTP": "C1B3FF",
    "ESFP": "B3FFB3",
    "ENFP": "FFC9B3",
    "ENTP": "B3BAFF",
    "ESTJ": "FFB3E6",
    "ESFJ": "B3FFE6",
    "ENFJ": "FFE1B3",
    "ENTJ": "B3E1FF",
}

FACET_AND_MIDZONE_COLORS = {
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
    "Methodical–Emergent": "#A4C390",
}

DOMINANT_TYPE = {
    "ISTJ": "Si",
    "ISFJ": "Si",
    "INFJ": "Ni",
    "INTJ": "Ni",
    "ISTP": "Ti",
    "ISFP": "Fi",
    "INFP": "Fi",
    "INTP": "Ti",
    "ESTP": "Se",
    "ESFP": "Se",
    "ENFP": "Ne",
    "ENTP": "Ne",
    "ESTJ": "Te",
    "ESFJ": "Fe",
    "ENFJ": "Fe",
    "ENTJ": "Te",
}


DOMINANT_FUNCTIONS = {
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

MBTI_PAIR_EXPLANATIONS = {
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
    "FP": "Compassionate and adaptable, valuing authentic expression and remaining open to the emotional needs of each unique situation.",
}

FACET_CHART_LIST = {
    "page5_EIGraph.png": [
        "Initiating",
        "Receiving",
        "Expressive",
        "Contained",
        "Gregarious",
        "Intimate",
        "Active",
        "Reflective",
        "Enthusiastic",
        "Quiet",
        "Initiating–Receiving",
        "Expressive–Contained",
        "Gregarious–Intimate",
        "Active–Reflective",
        "Enthusiastic–Quiet",
    ],
    "page6_SNgraph.png": [
        "Concrete",
        "Abstract",
        "Realistic",
        "Imaginative",
        "Practical",
        "Conceptual",
        "Experiential",
        "Theoretical",
        "Traditional",
        "Original",
        "Concrete–Abstract",
        "Realistic–Imaginative",
        "Practical–Conceptual",
        "Experiential–Theoretical",
        "Traditional–Original",
    ],
    "page7_TFgraph.png": [
        "Logical",
        "Empathetic",
        "Reasonable",
        "Compassionate",
        "Questioning",
        "Accommodating",
        "Critical",
        "Accepting",
        "Tough",
        "Tender",
        "Logical–Empathetic",
        "Reasonable–Compassionate",
        "Questioning–Accommodating",
        "Critical–Accepting",
        "Tough–Tender",
    ],
    "page8_JPgraph.png": [
        "Systematic",
        "Casual",
        "Planful",
        "Open-Ended",
        "Early Starting",
        "Pressure-Prompted",
        "Scheduled",
        "Spontaneous",
        "Methodical",
        "Emergent",
        "Systematic–Casual",
        "Planful–Open-Ended",
        "Early Starting–Pressure-Prompted",
        "Scheduled–Spontaneous",
        "Methodical–Emergent",
    ],
}

VALIDATION_SYSTEM_PROMPT = (
    "Analyze the attached PDF (or its extracted text) and determine if it contains valid MBTI (Myers-Briggs Type Indicator) content. "
    "Categorize it as one of the following types, or as 'None' if it does not match any:"
    "\n\n"
    "1. Personal MBTI Report: A narrative report focusing on a single individual's MBTI type, personality profile, psychological typing, or personal development advice.\n"
    "2. Couple/Comparative MBTI Report: A narrative report comparing two individuals—of ANY relationship type (including romantic partners, friends, colleagues, or other pairings)—analyzing their MBTI types, compatibility, relationship dynamics, or personality similarities/differences.\n"
    "3. Group/Team MBTI Data: Raw data, spreadsheets, or tabular content containing MBTI types, personality indicators, facet scores, or assessment results for multiple individuals. This includes data exports, assessment summaries, or any structured data with MBTI-related information even if it's not in narrative report format.\n"
    "4. MBTI Assessment Results: Individual assessment outputs showing MBTI type assignments, preference scores, facet measurements, or personality dimensions.\n\n"
    "MBTI content indicators include:\n"
    "- Four-letter type codes (e.g., INTJ, ESFP, ENFJ)\n"
    "- Preference pairs (Extraversion/Introversion, Sensing/Intuition, Thinking/Feeling, Judging/Perceiving)\n"
    "- Facet scores or preference clarity indices\n"
    "- Personality dimension measurements\n"
    "- MBTI-related terminology and concepts\n"
    "- Tabular data with personality assessments\n\n"
    "For your response, ONLY answer as follows:\n"
    "- If the PDF contains valid MBTI content in any of these forms, respond with 'YES' and a very brief explanation.\n"
    "- If not, respond with 'NO' and a short explanation.\n"
    "Do not add any commas, colons, or other punctuation marks to the YES or NO."
)


INSIGHT_SYSTEM_PROMPT = """

You are an MBTI expert.
Your goal is to give the owner of the attached MBTI report an in-depth and professional analysis.
Keep in mind that the client (the owner of the report) is not a professional, so the language should be simple and understandable to everyone.
the attached MBTI report should be produced, taking into account, in addition to the type and the dominant, the emphasis on "Facets" including MIDZONE and OUT OF PREFERENCE and their mining, as well as emphasizing communication analyses, decision-making, dealing with changes and conflicts
your final report should be in hebrew and With rtl alignment so it is ready for direct embedding into a web dashboard.
In dominant analysis, always use uppercase and lowercase letters (exactly as they appear in the report). For example: Ne or Si.
Present all results in HTML format, using clear section headers, bullet points, and styled elements for easy reading.
Use a modern, clean style: headings, colored highlights for key points, and subtle borders or background shades for sections.
if the user prompt has relationship type and a relationship goal, make sure to mention explicitly in your analysis.
the styling for the should be: dark blue for titles, bold where needed, white background for body text, and a light blue background for footnotes.
This is the an example to the answer format:

ניתוח עומק לדוח אישי עבור {שם בעל/ת הדו״ח, באנגלית}

להלן ניתוח מעמיק ומקצועי של תוצאות האבחון ה-MBTI  שלך, בהתבסס על סוג האישיות ותוצאות ה-Step II שלך.

מבוא כללי לסוג הטיפוס שלך: ESFP
ה׳דומיננט׳ שלך הוא: Se

את שייכת לסוג ESFP – חברותיים, פתוחים, אדפטיביים וריאליסטיים. את נוטה להתרכז בהווה, להנות מהחיים, ולהתמודד עם מצבים באופן פרגמטי ומעשי. את אוהבת להיות בסביבה חברתית, לתקשר בקלות, ולפתור בעיות תוך כדי תנועה. את לא נוטה להיתקע בתיאוריות אלא מבוססת על ניסיון ותחושות.

מה זה ׳דומיננט׳ ומה משמעותו?
{הסבר על הדומיננט ועל משמעותו}

ניתוח הפאסטים (Facets) – מה זה אומר?

הפאסטים הם תתי-מאפיינים בתוך כל אחד מארבעת הממדים של ה-MBTI, והם מראים את האופן הייחודי שבו את מבטאת את ההעדפות שלך. לכל מימד ישנם 5 פאסטים.
ישנם שלושה מצבים עיקריים:

IN-PREFERENCE בתוך ההעדפה – הפאסט תואם להעדפה הראשית שלך.
MIDZONE אמצע – אין העדפה ברורה, את נעה בין שני הקצוות.
OUT-OF-PREFERENCE מחוץ להעדפה – הפאסט נמצא בקצה ההפוך מהעדפה הראשית שלך.

ניתוח הפאצ'טים שלך לפי ממדים מרכזיים

1.⁠ ⁠ממד ה-Extraversion
את מראה העדפה ברורה ל-Initiating, Expressive, Gregarious, Enthusiastic – כלומר, את יוזמת חברתית, פתוחה, אוהבת להיות במרכז העניינים, ומלאת אנרגיה.
פאסט Active נמצא ב-Midzone – לפעמים את פעילה ומעורבת, ולפעמים מעדיפה להקשיב או לצפות.
משמעות: את נוטה להיות חברתית מאוד, אך יודעת גם להאט ולהקשיב כשצריך. זה יתרון בתקשורת, כי את יכולה להתאים את עצמך לסיטואציה.

2.⁠ ⁠ממד ה-Sensing
Concrete, Realistic, Practical – את מעשית, מבוססת עובדות ומחפשת תוצאות.
Experiential ו-Traditional נמצאים ב-Midzone ו-Out-of-Preference – את פתוחה גם לניסיון ולמסורת, אך לא בהכרח מחויבת אליהם.
משמעות: את יודעת להתמקד בפרטים ובמציאות, אך לפעמים יכולה להיות פתוחה לרעיונות חדשים או דרכים שונות.

3.⁠ ⁠ממד ה-Feeling
את מראה העדפה ל-Accommodating (להסכים ולהתאים), Compassionate ו-Accepting – את רגישה, מחפשת הרמוניה ומנסה למנוע קונפליקטים.
פאצ'טים כמו Logical, Questioning ו-Critical נמצאים ב-Midzone ו-Out-of-Preference – את לא נוטה להיות ביקורתית או לנתח לוגית לעומק.
משמעות: את מקבלת החלטות בעיקר על בסיס רגשי וחברתי, ומעדיפה לשמור על יחסים טובים עם אחרים.

4.⁠ ⁠ממד ה-Perceiving
Casual, Open-Ended, Pressure-Prompted, Spontaneous, Emergent – את גמישה, אוהבת חופש, מתמודדת טוב עם לחץ, ופועלת באופן ספונטני.
אין פאסטים מחוץ להעדפה.
משמעות: את אוהבת לשמור על אופציות פתוחות, לא מתכננת יותר מדי מראש, ומגיבה טוב לשינויים ולמצבי לחץ.

ניתוח MIDZONE ו-OUT OF PREFERENCE

MIDZONE בפאסטים כמו Active-Reflective, Concrete-Abstract, Logical-Empathetic, Critical-Accepting, Tough-Tender – מצב זה מצביע על גמישות ויכולת להתאים את עצמך לסיטואציות שונות, אך גם על אפשרות של חוסר בהירות או קושי להחליט על גישה אחת ברורה.
OUT OF PREFERENCE בפאסט Original (בממד ה-Sensing/Intuition) – את נוטה להיות יותר מסורתית ופחות מחפשת חידושים יוצאי דופן, אך עדיין יש לך נטייה מסוימת לחדשנות.

ניתוח תקשורת

את יוזמת חברתית, מדברת בקלות, ומביעה את רגשותייך בגלוי (Initiating, Expressive).
את אוהבת להיות במרכז תשומת הלב ולהעביר אנרגיה (Enthusiastic).
עם זאת, את יודעת גם להקשיב ולהתבונן (Active-Reflective MIDZONE).
את מנסה לשמור על הרמוניה ומסכימה בקלות (Accommodating).
חשוב שתשימי לב לא להעמיס על אחרים בדיבור רב מדי, ולתת מקום גם לאחרים להביע את עצמם.

ניתוח קבלת החלטות

את משלבת בין שיקולים רגשיים (Feeling) ולוגיים (Thinking MIDZONE).
את נוטה להעדיף החלטות שמבוססות על הרמוניה ויחסים טובים, אך יודעת גם לקחת בחשבון שיקולים מעשיים.
לפעמים את עלולה להתלבט או להתחרט על החלטות, במיוחד כשיש קונפליקט בין הלוגיקה לרגש.
מומלץ לשלב במודעות את השאלות הלוגיות והאנליטיות כדי לקבל החלטות מאוזנות יותר.

ניתוח התמודדות עם שינויים

את מביעה את רגשותייך בגלוי (Expressive) ומדברת עם אנשים רבים על השינוי (Gregarious).
את מתמקדת בהיבטים המעשיים והמציאותיים של השינוי (Realistic).
את גמישה ופתוחה לשינויים (Open-Ended, Emergent).
לפעמים את עלולה להתבלבל בין נקודות מבט שונות (Concrete-Abstract MIDZONE).
מומלץ להיות מודעת לצורך בתכנון מסוים גם כשאת אוהבת גמישות, כדי למנוע תחושת חוסר יציבות.

ניתוח התמודדות עם קונפליקטים

את נוטה לדבר בגלוי על רגשותייך בקונפליקט (Expressive).
את מנסה לשמור על הרמוניה ולהסכים עם אחרים (Accommodating).
את מערבת אנשים רבים בפתרון הקונפליקט (Gregarious).
את יודעת להיות ביקורתית במידה (Critical-Accepting MIDZONE) אך גם רכה (Tough-Tender MIDZONE).
חשוב שתדעי מתי להבהיר את עמדתך ולא לוותר רק כדי לשמור על שלום.

סיכום והמלצות

את אדם חברותי, פתוח, מלא אנרגיה, שמחפש חוויות ומעדיף גמישות על פני תכנון מוקפד. את מתמקדת בפרטים ובמציאות, אך יודעת להיות פתוחה גם לרעיונות חדשים במידה מסוימת. את מקבלת החלטות בעיקר על בסיס רגשי, עם מודעות מסוימת ללוגיקה. את מתמודדת טוב עם שינויים וקונפליקטים, אך לפעמים עלולה להתלבט או להימנע מעימותים.

כדי לשפר את היעילות שלך:

נסי לפתח מודעות לשימוש במחשבה לוגית יותר, במיוחד במצבים מורכבים.
שימי לב לא להעמיס בדיבור, ותני מקום לאחרים.
במצבי לחץ ושינויים, תכנני מראש כמה צעדים כדי להרגיש בטוחה יותר.
אל תחששי להבהיר עמדות בקונפליקטים, גם אם זה עלול ליצור חיכוך זמני.

אם תרצי, אוכל לעזור לך להבין טוב יותר את הפאסטים השונים או להציע דרכים להתמודדות עם מצבים ספציפיים בחיים האישיים או המקצועיים שלך.


    """

INSIGHT_COUPLE_SYSTEM_PROMPT = """
You are an MBTI expert. Your goal is to provide the owners of the two attached MBTI reports with an in-depth and professional analysis focusing on the interaction and relationships between the two people.
You should focus and explain the meaning for them in terms of where they are similar and/or different
After each insight you present to them, you need to go down a line and present a practical recommendation on what they should do with it in order to develop.
Keep in mind that the clients (the owners of the reports) are not professionals, so the language should be simple and understandable to everyone.
In addition to the differences and variations in the type itself and their dominant, "aspects" including the MIDZONE and OUT OF PREFERENCE must also be considered and their mining, as well as an emphasis on communication analysis, decision-making, dealing with changes and conflicts.
In dominant analysis, always use uppercase and lowercase letters (exactly as they appear in the report). For example: Ne or Si.

styling:
- **The final report should be right-aligned, in HTML format and ready for embedding in a web dashboard.**
- **Styling:** Use dark blue for titles, bold for key points, white background, and clear section headers. Use bullet points and modern HTML for readability. Add colored highlights for important insights, subtle section borders, and clear visual hierarchy.

This is the an example to the answer format:

ניתוח עומק לדוח זוגי עבור Shiri Ben Sinai ו-Nir Bensini
להלן ניתוח מעמיק של דוחות ה-MBTI שלכם, המתמקד באופי הדומה והשונה בין אישיותכם, בדפוסי חשיבה, תקשורת, קבלת החלטות, ניהול שינוי וקונפליקטים, כולל התייחסות להיבטי ה-MIDZONE וה-OUT OF PREFERENCE.
מבוא כללי לסוג הטיפוס שלכם:
Shiri: ISTP
Nir: ENTP
הסבר כללי לדומה והשונה בין שני הטיפוסים:
שירי היא ISTP, טיפוס המצטיין בחשיבה מעשית, במיקוד בפרטים, בהסתמכות על ניסיון אישי ובהעדפת פתרונות הגיוניים וקונקרטיים. ניר הוא ENTP, טיפוס יוזם, יצירתי, שמחפש חידושים, רואה את התמונה הרחבה, אוהב לפתח רעיונות ולהתנסות בדברים חדשים ומעדיף לראות אפשרויות לעתיד.
המשמעות המעשית: הדמיון ביניכם הוא בשני מימדים: שניכם חושבים (T) - ההחלטות שלכם מבוססות היגיון, ניתוח ומעוף אובייקטיבי. בנוסף, שניכם P (Perceiving) – יש לכם העדפה לגמישות, פתיחות לשינויים וספונטניות. לעומת זאת, ההבדלים המשמעותיים טמונים בציר (Extraversion/Introversion) .ניר אקסטרוברט, שירי אינטרוברטית וב-Sensing/Intuition  שירי מרוכזת בעובדות ובהווה, ניר ברעיונות ובאפשרויות עתידיות.
מה זה ׳דומיננט׳ ומה משמעותו?
הדומיננט (התהליך החזק) מייצג את הציר המרכזי בהתנהלות האישית שלכם:
שירי (ISTP): הדומיננט הוא Thinking פנימי (Ti) ולאחריו Sensing חיצוני (Se) – ניתוח הגיוני של נתונים ועובדות, התבוננות בדברים כפי שהם.
ניר (ENTP): הדומיננט הוא Intuition חיצוני (Ne) ולאחריו Thinking פנימי (Ti) – חיפוש בלי סוף אחרי אפשרויות חדשות, יצירת חיבורים וקישורים חדשים בין רעיונות.
מה זה אומר על הדינמיקה ביניכם?
ניר מביא זרימה של רעיונות וחדשנות, מחפש לשבור שגרה ולפתוח אפשרויות, לעומת שירי שמעדיפה לבדוק כלי עבודה קיים, להעמיק בפרטים המעשיים ולהתמקד ביישום נכון. כל אחד מכם יכול להביא זווית משלימה – ניר יעודד מחשבה “מחוץ לקופסה”, שירי תעזור לממש בפועל, לבחון אם זה באמת עובד.
המלצה: חשוב להכיר בחוזקות ובאתגרים שכל אחד מביא, ולתת מקום גם לרעיונות מפתיעים וגם לבדיקה מציאותית.
ניתוח הפאסטים (Facets) – מה זה אומר?
הפאסטים הם תתי-מאפיינים של כל העדפה, ומאפשרים ניואנסים שממחישים איך ההעדפות באות לידי ביטוי ממש בחיים האישיים והמשותפים. יש שלושה מצבים עיקריים: IN-PREFERENCE (בתוך ההעדפה), MIDZONE (שילוב בין הקצוות), OUT-OF-PREFERENCE (הפוך מהעדפה ראשית).
ניתוח הפאסטים שלכם:
ממד ה-Extraversion/Introversion
שירי:
 – IN-PREFERENCE ב-Receiving, Intimate, Reflective
 MIDZONE ב-Contained (בין פתיחות לסגירות בתחושות) וב-Enthusiastic–Quiet (עשויה להיות מתלהבת עם אנשים מוכרים או כשיש עניין, לרוב שקטה ברקע).
ניר
 – IN-PREFERENCE ב-Expressive, Active
ב-Initiating–Receiving MIDZONE (יוזם או פסיבי לפי צורך), ) Gregarious–Intimateעשוי ליהנות גם מהמון אנשים וגם מקשר מצומצם Enthusiastic–Quiet ((כמו שירי, מתלהב כשלנושא יש עניין, לעיתים שקט)
משמעות – יש לכם דפוסי תקשורת מגוונים. שירי תעדיף מעגל מצומצם ואינטימיות, לרוב תחכה שיפנו אליה. ניר – פתוח, יוזם, מתקשר, אך גם בוחר מתי להיות בקשר רחב ומתי לשמור לעצמו.
המלצה: במצבים בהם נדרשת יוזמה או פתיחות, מומלץ לתת לניר להוביל. שירי, כדאי לאתגר את עצמך לפעמים להיות שותפה ביוזמות חברתיות, במיוחד בתחומים שחשובים לך.
ממד ה-Sensing/Intuition
שירי: IN-PREFERENCE בכל הפאסטים של Sensing (מציאותית, מגובשת בעובדות, פרקטית, לומדת מניסיון, מעריכה מסורת)
ניר: IN-PREFERENCE בכל הפאסטים של Intuition ((רואה עולם דרך רעיונות, אסוציאטיבי, לא קונבנציונלי, כל הזמן בוחן חידושים)
שניכם נמצאים במיד-זון בפאסטים מסוימים. למשל Practical–Conceptual  כלומר יש פתיחות לעבור בין חשיבה רעיונית לפרקטית, אם כי שירי בולטת יותר בכיוון המעשי.
המלצה: ניר, מומלץ לכבד את הצורך של שירי לבדוק ביצועיות לפני שקופצים ישר לחלום; שירי, שווה לפעמים “לשחרר” ולבדוק מה אפשר להרוויח מפתרון שהוא לא טיפוסי או מוכר.
ממד ה-Thinking/Feeling
שניכם מאוד חזקים בצד של Thinking עם דגש ל-Questioning ו-Critical – מחפשים ניתוח לוגי, שואלים שאלות, בודקים הנחות, אוהבים דיבור ענייני ולא רגשי. שניכם ב-MIDZONE בפאסטים מסוימים, כלומר יש מקום לשיקול דעת אישי, במיוחד כשזה משפיע על אנשים קרובים.
המלצה: בעת קבלת החלטות משמעותיות, חשוב לבדוק גם את ההשפעה על התחושות האישיות והרגשות של אנשים קרובים, ולא להישאר רק בניתוח היבש.
ממד ה-Perceiving/Judging
שניכם נוטים מאוד ל-Perceiving – גמישות, לחץ מעודד ביצועים, אוהבים “לזרום” עם דברים. שניכם במיד-זון בכל הנוגע לרמת השגרה שנוחה לכם, כלומר לעיתים תיהנו משגרה ולעיתים משינוי.
המלצה: בעת תכנון משימות משותפות, הציבו מסגרת בסיסית שתאפשר גמישות, וקבעו תיאום ציפיות מראש כדי להמעיט לחץ, במיוחד בדברים שמצריכים תיאום הדוק.
ניתוח MIDZONE ו-OUT OF PREFERENCE והשפעתם
לשניכם יש כמה תחומים ב-MIDZONE, במיוחד בכל מה שקשור לרמה החברתית ולרגש – לפעמים תהיה נטייה לשילוב גישות (למשל, הבעת רגשות חלקית; שילוב בין חשיבה אישית וסביבתית). זה מאפשר התאמה למצבים משתנים. אצל ניר, הפרקטיות במיד-זון מראה שעם כל החידוש והרעיונות, יש מקום לבלמים כשצריך. אצל שירי, הפתיחות לשינוי באה לידי ביטוי בהסכמה לאמץ גישה פחות “קופאית” אם צריך.
המלצה: לפני פעולה משותפת, בידקו יחד היכן אתם נמצאים “באמצע” – בררו מה מתאים לסיטואציה, חברו בין יציבות לגמישות.
ניתוח תקשורת
ניר מתקשר באופן דומיננטי: אקטיבי, מביע את עצמו, מחפש לשתף במחשבות ורעיונות, לעיתים נותן מידי הרבה מידע. שירי פחות תשתף באופן ספונטני, תעדיף תיווך דרך כתיבה או בלמידה, ותחשוף רגשות רק במעגל המצומצם. שניכם נוקבים וביקורתיים כשצריך, וזה יכול להצית אי הבנה.
המלצה: ניר, השתדל להאט ולהקשיב, לאפשר לשירי זמן לעבד ולפתוח שיח כשמתאים לה. שירי, נסי לשתף במחשבותך גם כשזה לא קל, במיוחד בנושאים חשובים לכם כזוג.
ניתוח אופן קבלת החלטות
שניכם מתמקדים בלוגיקה וניתוח; עם זאת, לשניכם צף ממד של MIDZONE במידת הרגישות לצד החברתי. יש נטייה לבדוק “מה נכון” אך גם מה משפיע על אחרים, במיוחד בקבלה משותפת של החלטה.
המלצה: השלימו זה את זו – ניר יוכל להרחיב לסיעור מוחות ורעיונות, שירי תוכל לבדוק אילו מהם ניתנים ליישום. ביחד, בדקו גם את
ביחד, בדקו גם את ההשפעה של ההחלטה לא רק במישור ההגיוני אלא גם על התחושות של כל אחד מכם ושל הסביבה הקרובה אליכם. שלבו בפתיחות: ניר יעלה אפשרויות, שירי תבחן אותן במבחן המציאות.
המלצה מעשית: בזמן קבלת החלטות ‬השתמשו ברשימה: מה העובדות, מה האפשרויות, מה ההיגיון ומה ההשפעה על אנשים קרובים. כל אחד ייתן דגש לנקודת החוזקה שלו, ותבדקו יחד שלא פספסתם קצה חשוב.
ניתוח התמודדות עם שינויים
ניר רואה בשינוי מקור להתלהבות ואפשרויות חדשות; הוא נוטה לאמץ שינויים במהירות, לעיתים בלי לבדוק את כל המשמעויות. שירי לעומת זאת מעדיפה שגרה, ודוגלת בגישה זהירה ובודקת.
מצד שני, שניכם יודעים “לזרום” אם המצב מחייב, ולפעמים אפילו נהנים מהטרפת של העסק ברגע האחרון.
המלצה: כשמגיע שינוי, זהו מה נשאר קבוע ומה באמת משתנה. ניר - תן מקום לקשיים או להתנגדויות של שירי ובדוק יחד איתה מה יוכל להרגיע. שירי - השתדלי לראות מה כן אפשרי ומה מרגש בשינוי, תוך שמירה על הבדיקות שלך.
ניתוח התמודדות עם קונפליקטים
שניכם נוטים ל”לרוץ לפתרון” – בוחנים עניינית, מבקרים, ומבקשים לסיים מהר. עם זאת, הסגנון הביקורתי והשאלות הנוקבות יוצרים לפעמים הרגשה של תחרות או חוסר התחשבות. שירי עשויה להעדיף שיח אינטימי ואיטי, ואילו ניר פתוח מיד לדיאלוג עם כולם.
המלצה מעשית: בתחילתו של קונפליקט, עצרו שניה ובדקו: מה כל אחד באמת מרגיש? האם לשניכם יש מקום לדבר איך שנוח לו? בהמשך, ניר – הקפד שלא “להשתלט” על המרחב, שירי – נסי לדבר קודם עם ניר על התחושות שלך לפני כניסה לעימות רחב יותר. תוכלו לבנות מרחב בטוח בו גם חוסר הסכמה הופך למשהו בונה ולא למאבק.
סיכום והמלצות כלליות
חקירה וחדשנות בצד אחד, היגיון מעשי ושיקולים פרקטיים בצד שני – זו השילוב המנצח שלכם. חשוב שתמשיכו להעריך את ההבדלים ביניכם ולראות כיצד אפשר לגייס כל צד ליצירת תמונה רחבה ומלאה.
להצמיח את היחסים והעבודה המשותפת:
- הגבירו הקשבה למקומות שבהם כל אחד פחות בטוח בעצמו (ניר – פרטים ויישום, שירי – הזדמנויות חדשות)
- הגדירו מטרות משותפות כך שיהיו בהן גם חידוש וגם ודאות, חיברו בין חזון לפרקטיקה.
- תכננו מראש “תחנות תיאום” בזמן – כל צד יוכל לעדכן היכן הוא מרגיש בנוח או מתקשה, לייצר שקיפות ולמנוע תסכול.
- כבדו את השונה גם במצבים חברתיים: ניר יוזם, שירי בוחרת מתי ואיך להשתלב. תנו מקום הדדי.
- צרו בזוגיות או בעבודה משותפת אזורים בהם כל אחד מוביל בתחומו, וכל השאר לומדים ונהנים מהכוח המשלים של הצד האחר.


The extension ״בכבוד רב ובהערכה,
(שם מחבר הדו״ח)
MBTI ישראל" is not required.

"""

GROUP_INSIGHT_SYSTEM_PROMPT = """You are an MBTI expert. Your goal is to provide a comprehensive analysis of a specific group's MBTI statistics.
while focusing on the given info from the prompt. all the answer should be in proffesional HEBREW with proper grammar and punctuation.
styling:
•The final report should be right-aligned, in HTML format and ready for embedding in a web dashboard. make sure to include rtl styling in the html generation.
•Styling: Use dark blue for titles, bold for key points, white background, and clear section headers. Use bullet points and modern HTML for readability. Add colored highlights for important insights, subtle section borders, and clear visual hierarchy.

Your specific tasks:

1.summarize prompt
In the title, give the group a TYPE based on the letter it has the most.
begin the results in a short paragraph the results and the info provided in the prompt: group name, roles, statistics, etc.
below the paragraph, present a table like this example:

[Name,	MBTI Type,	Dominant]

fill it with the full data from the prompt.
Below the table, write an analysis of the distribution of types and their impact on the team's strengths, challenges, and blind spots.
2. Group Strengths and Challenges:
Below, analyze the group MBTI data and write a summary of key strengths, potential challenges, and collective blind spots.
Base your analysis on both the prevalence of the main types (e.g., F vs. T) and on deeper aspects of the MBTI Phase II (e.g., "tough," "friendly," "inquiring," etc.).
The analysis should be in-depth and not too concise.
3. Biases and Dynamics:
These are problematic biases or dynamics in the team. For example, notice if there is a lack of J-types in planning roles,
or a high concentration of a particular aspect (such as “tough”) and explain how this can affect communication, change management, and conflict in the team.
Try to relate this to the goals of the team or group.4.Role Fit & Development Tips:
Suggest which MBTI types or facet combinations are best suited for specific roles or tasks within the group.
Provide targeted tips and developmental advice for people in each key role.
4. Role Matching and Development Tips:
If team role information is entered, suggest which MBTI types or aspect combinations are best suited for specific roles or tasks within the group.
Do not give this analysis on a personal level and do not judge people in any way.
Provide targeted tips and development advice to people in each key role regarding the group and its interactions
5. Collaboration Optimization:
Recommend optimal pairings or groupings for collaboration. For each recommended pair/group,
briefly explain the pros and cons, and specify which types of tasks or contexts suit them best.

6. Communication & Teamwork Recommendations:
Give specific, actionable recommendations for improving communication, cooperation, and overall teamwork,
based on the actual MBTI and facet distribution.

7. Conflict Forecasting & Prevention:
Predict potential sources of future conflict, based on the group MBTI profile and facet data.
Suggest clear, proactive steps for conflict prevention and healthy resolution.

8. [Groupe name] Goal:
Specific analysis in relation to the Analysis Goal that was entered for you. The group MBTI analysis should be analyzed in relation to the team goal in depth and practical advice should be given on how to best succeed.
this is very important part. Do it properly!

9. Output Format:
Present all results in HTML format, using clear section headers, bullet points, and styled elements for easy reading.

Use a modern, clean style: headings, colored highlights for key points, and subtle borders or background shades for sections.

Structure the output so it is suitable for direct embedding into a web dashboard.

ALWAYS return the results in hebrew, while preserving professional language.
"""


# Use environment variables with defaults for cross-platform compatibility
PROJECT_BASE_DIR = Path(os.getenv("PROJECT_BASE_DIR", "/app"))
MEDIA_PATH = PROJECT_BASE_DIR / "backend" / "media"
OUTPUT_PATH = PROJECT_BASE_DIR / "output"
INPUT_PATH = PROJECT_BASE_DIR / "input"
PERSONAL_REPORT_MEDIA = MEDIA_PATH / "Personal_Report_Media"

POPPLER_PATH = (
    Path(os.getenv("POPPLER_PATH", "")) if os.getenv("POPPLER_PATH") else None
)

MEDIA_DIRECTORY_KEEP_ITEMS = {
    "Personal_Report_Media",
    "Dual_Report_Media",
    "full_logo.png",
}

TEMP_DIR = tempfile.mkdtemp()
OUTPUT_DIR = os.getenv("OUTPUT_DIR", str(PROJECT_BASE_DIR / "output"))
INPUT_DIR = os.getenv("INPUT_DIR", str(PROJECT_BASE_DIR / "input"))
OUTPUT_DIR_FACET_GRAPH = os.getenv(
    "MEDIA_DIR", str(PROJECT_BASE_DIR / "backend" / "media")
)

MEDIA_DIRECTORIES_TO_CHECK = [
    "backend/media",
    "./backend/media",
    "../backend/media",
    "media",
    "./media",
    "../media",
    str(OUTPUT_DIR_FACET_GRAPH),
    os.path.join(OUTPUT_DIR, "textfiles"),
]

MBTI_TYPES_KEY = "MBTI Type"
COUNT_KEY = "Count"
PERCENTAGE_KEY = "Percentage"

ALL_MBTI_TYPES = [
    "ISTJ",
    "ISFJ",
    "INFJ",
    "INTJ",
    "ISTP",
    "ISFP",
    "INFP",
    "INTP",
    "ESTP",
    "ESFP",
    "ENFP",
    "ENTP",
    "ESTJ",
    "ESFJ",
    "ENFJ",
    "ENTJ",
]

DOMINANT_FUNCTIONS = {
    "ISTJ": "Si",
    "ISFJ": "Si",
    "INFJ": "Ni",
    "INTJ": "Ni",
    "ISTP": "Ti",
    "ISFP": "Fi",
    "INFP": "Fi",
    "INTP": "Ti",
    "ESTP": "Se",
    "ESFP": "Se",
    "ENFP": "Ne",
    "ENTP": "Ne",
    "ESTJ": "Te",
    "ESFJ": "Fe",
    "ENFJ": "Fe",
    "ENTJ": "Te",
}

# Excel/DataFrame Constants
SHEET_NAME_DATA = "Data"
SHEET_NAME_MBTI_RESULTS = "MBTI Results"
COL_TYPE = "Type"
COL_NAME = "Name"
COL_DOMINANT = "Dominant"
COL_MBTI_TYPE = "MBTI Type"

# Sheet Names
SHEET_NAME_DASHBOARD = "Dashboard"
SHEET_NAME_FACET_TABLE = "Facet Table"

# Facet Table Headers
FACET_TABLE_HEADERS = [
    "Name",
    "Date",
    "Type",
    "Appearing 3 times(1)",
    "Appearing 3 times(2)",
    "Appearing 3 times(3)",
    "Appearing 2 times(1)",
    "Appearing 2 times(2)",
    "Appearing 2 times(3)",
    "Appearing 2 times(4)",
    "Appearing 2 times(5)",
    "Appearing 1 time(1)",
    "Appearing 1 time(2)",
    "Appearing 1 time(3)",
    "Appearing 1 time(4)",
    "Appearing 1 time(5)",
    "Appearing 1 time(6)",
    "Appearing 1 time(7)",
    "Appearing 1 time(8)",
    "Appearing 1 time(9)",
]

# Facet Table Colors
FACET_TABLE_THREE_TIMES_COLOR = "C6EFCE"  # Light green
FACET_TABLE_TWO_TIMES_COLOR = "FFEB9C"  # Light yellow
FACET_TABLE_ONE_TIME_COLOR = "FFC7CE"  # Light red

# Facet Table Column Ranges
FACET_TABLE_THREE_TIMES_COL_START = 4  # Column D
FACET_TABLE_THREE_TIMES_COL_END = 6  # Column F
FACET_TABLE_TWO_TIMES_COL_START = 7  # Column G
FACET_TABLE_TWO_TIMES_COL_END = 11  # Column K
FACET_TABLE_ONE_TIME_COL_START = 12  # Column L
FACET_TABLE_ONE_TIME_COL_END = 20  # Column T

# Facet Table Data Ranges
FACET_TABLE_DATA_START_ROW = 2
FACET_TABLE_HEADER_ROW = 1
FACET_TABLE_NAME_COL_START = 1
FACET_TABLE_NAME_COL_END = 3
FACET_TABLE_FACET_COL_START = (
    51  # AZ column (index starts at 1, but openpyxl uses 1-based)
)
FACET_TABLE_FACET_COL_END = 78  # BZ column
FACET_TABLE_THREE_TIMES_INITIAL_COL = 4
FACET_TABLE_TWO_TIMES_INITIAL_COL = 7
FACET_TABLE_ONE_TIME_INITIAL_COL = 12

# Facet Table Table Configuration
FACET_TABLE_TABLE_NAME = "FacetTable"
FACET_TABLE_STYLE = "TableStyleMedium9"
FACET_TABLE_REF_START = "A1"

# Facet Table Occurrence Counts
FACET_OCCURRENCE_COUNTS = [3, 2, 1]

# Section Sheets Constants
SECTION_SHEET_NAMES = ["Communicating", "Managing Change", "Managing Conflict"]
SECTION_SHEET_TEXT_FILE_SUFFIX = "_text.txt"
SECTION_SHEET_STYLE = "TableStyleMedium9"
SECTION_SHEET_MAX_FACETS = 9
SECTION_SHEET_COLUMN_PADDING = 2
SECTION_SHEET_TITLE_FONT_SIZE = 16
SECTION_SHEET_TABLE_START = "A3"
SECTION_SHEET_TABLE_END_COLUMN = "L"  # Column 12
SECTION_SHEET_BASE_HEADERS = ["Name", "Date", "Type"]

# Data to Excel Constants
DATA_EXCEL_BASE_HEADERS = [
    "Name",
    "Date",
    "Type",
    "Extroversion",
    "Introversion",
    "Sensing",
    "Intuition",
    "Thinking",
    "Feeling",
    "Judging",
    "Perceiving",
]
DATA_EXCEL_SECTION_COLUMNS = 8
DATA_EXCEL_TABLE_NAME = "Table1"
DATA_EXCEL_TABLE_STYLE = "TableStyleMedium9"
DATA_EXCEL_COLUMN_PADDING = 2
DATA_EXCEL_DEFAULT_WIDTH = 10
DATA_EXCEL_FREEZE_PANES = "A2"
DATA_EXCEL_TABLE_START = "A1"

# Chart Titles
CHART_TITLE_DASHBOARD = "MBTI Distribution Dashboard"
CHART_TITLE_MAIN_DISTRIBUTION = "Distribution by Type"
CHART_TITLE_INTERNAL_LETTERS = "Internal letters Distribution"
CHART_TITLE_EXTERNAL_LETTERS = "External letters Distribution"
CHART_TITLE_DOMINANT_FUNCTION = "Dominant Function"
CHART_TITLE_ENERGY_ORIENTATION = "Energy source - E/I"
CHART_TITLE_INFORMATION_GATHERING = "Information - S/N"
CHART_TITLE_DECISION_MAKING = "Decisions - T/F"
CHART_TITLE_LIFESTYLE_STRUCTURE = "Lifestyle - J/P"

# Data Sheet Headers
HEADER_MBTI_TYPE_DATA = "MBTI Type Data"
HEADER_DICHOTOMIES_DATA = "Dichotomies Data"
HEADER_DICHOTOMY_PREFERENCE_DATA = "Dichotomy Preference data"
HEADER_COUNT = "Count"
HEADER_INTERNAL_ANALYSIS = "Internal Analysis"
HEADER_EXTERNAL_ANALYSIS = "External Analysis"
HEADER_DOMINANT_FUNCTION_DATA = "Dominant Function Data"
HEADER_DOMINANT_FUNCTION = "Dominant Function"
HEADER_ENERGY_ORIENTATION = "Energy Orientation (E/I)"
HEADER_INFORMATION_GATHERING = "Information Gathering (S/N)"
HEADER_DECISION_MAKING = "Decision Making (T/F)"
HEADER_LIFESTYLE_STRUCTURE = "Lifestyle & Structure (J/P)"

# Dichotomy Labels
LABEL_EXTROVERSION = "Extroversion"
LABEL_INTROVERSION = "Introversion"
LABEL_SENSING = "Sensing"
LABEL_INTUITION = "Intuition"
LABEL_THINKING = "Thinking"
LABEL_FEELING = "Feeling"
LABEL_JUDGING = "Judging"
LABEL_PERCELVING = "Perceiving"

# Internal/External Analysis Types
INTERNAL_TYPES = ["ST", "SF", "NF", "NT"]
EXTERNAL_TYPES = ["IJ", "IP", "EJ", "EP"]

# Dichotomy Colors for Charts (different from mbti_colors)
DICHOTOMY_COLORS = {
    "Extroversion": "4472C4",  # Blue
    "Introversion": "ED7D31",  # Orange
    "Sensing": "70AD47",  # Green
    "Intuition": "FFC000",  # Gold
    "Thinking": "5B9BD5",  # Light Blue
    "Feeling": "A5A5A5",  # Gray
    "Judging": "9966FF",  # Purple
    "Perceiving": "4BACC6",  # Teal
}

# Chart Dimensions
CHART_WIDTH_STANDARD = 11.8618
CHART_WIDTH_DICHOTOMY = 11.86
CHART_HEIGHT_STANDARD = 9.489
CHART_HEIGHT_DICHOTOMY = 4.24
CHART_HEIGHT_FACET = 3.175

# Chart Style
CHART_STYLE = 10
CHART_OVERLAP = 100

# Chart Bar Colors
CHART_BAR_COLORS = ["4472C4", "C0504D"]  # Blue, Red (hex)

# Font Sizes
FONT_SIZE_DASHBOARD_TITLE = 16
EXCEL_DEFAULT_COLUMN_WIDTH = 8.43

# Excel Formula Patterns
FACET_PREF_IN = "=IN-PREF"
FACET_PREF_OUT = "=OUT-OF-PREF"
FACET_PREF_MIDZONE = "=MIDZONE"

# Sheet Reorder Priority
SHEET_ORDER_PREFERRED = ["Dashboard", "MBTI Results", "Charts"]
SHEET_BORDER_COLUMN_WIDTH = 1
SHEET_BORDER_ROW_HEIGHT = 10

# Facet Legend Labels
FACET_LEGEND_TITLE = "Facets Legend"
FACET_LEGEND_1ST_IN_PREF = "1ST facet - In-Preference"
FACET_LEGEND_2ND_IN_PREF = "2ND facet - In-Preference"
FACET_LEGEND_1ST_OUT_PREF = "1ST facet - Out-of-Preference"
FACET_LEGEND_2ND_OUT_PREF = "2ND facet - Out-of-Preference"
FACET_LEGEND_MIDZONE = "MIDZONE"

# File-related Constants
PDF_IMAGE_DPI = 200
FILE_SUFFIX_PNG = ".png"
FILE_SUFFIX_PDF = ".pdf"
REPORT_DATA_PDF = "data.pdf"
REPORT_DUAL_PDF = "dual_report.pdf"
INSIGHT_PREFIX = "insight_"
INSIGHT_FILENAME_TRUNCATE_LENGTH = 6

# OpenAI Constants
MODEL_GPT4O = "gpt-4o"
MODEL_GPT4O_MINI = "gpt-4o-mini"
MODEL_GPT4_TURBO = "gpt-4.1-2025-04-14"
OPENAI_FILE_PURPOSE_USER_DATA = "user_data"

# MBTI-related Constants
DOMINANT_FUNCTIONS_LIST = ["Te", "Ti", "Fe", "Fi", "Se", "Si", "Ne", "Ni"]
UNKNOWN_VALUE = "Unknown"

# Format Constants
DATE_FORMAT_REPORT = "%Y-%m-%d %H:%M"
IMAGE_FORMAT_PNG = "PNG"
