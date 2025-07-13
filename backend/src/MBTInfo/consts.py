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
    "Analyze the attached PDF (or its extracted text) and determine if it is a valid MBTI (Myers-Briggs Type Indicator) report. "
    "Categorize it as one of the following types, or as 'None' if it does not match any:"
    "\n\n"
    "1. Personal MBTI Report: Focuses on a single individual's MBTI type, their personality profile, psychological typing, or personal development advice.\n"
    "2. Couple/Comparative MBTI Report: Compares two individuals (e.g., couple, friends, colleagues, partners), analyzing their MBTI types, compatibility, relationship dynamics, or personality similarities/differences.\n"
    "3. Group/Team MBTI Report: Analyzes three or more individuals as a group or team, reporting on group dynamics, overall type distribution, team strengths, or collaborative advice based on MBTI profiles.\n\n"
    "For your response, ONLY answer as follows:\n"
    "- If the PDF matches one of these types, respond with 'YES' and a very brief explanation.\n"
    "- If not, respond with 'NO' and a short explanation."
)

INSIGHT_SYSTEM_PROMPT = ("""

You are an MBTI expert. 
Your goal is to give the owner of the attached MBTI report an in-depth and professional analysis. 
Keep in mind that the client (the owner of the report) is not a professional, so the language should be simple and understandable to everyone.
the attached MBTI report should be produced, taking into account, in addition to the type and the dominant, the emphasis on "Facets" including MIDZONE and OUT OF PREFERENCE and their mining, as well as emphasizing communication analyses, decision-making, dealing with changes and conflicts
your final report should be in hebrew and With right alignment so it is ready for direct embedding into a web dashboard.
In dominant analysis, always use uppercase and lowercase letters (exactly as they appear in the report). For example: Ne or Si.

Present all results in HTML format, using clear section headers, bullet points, and styled elements for easy reading.
Use a modern, clean style: headings, colored highlights for key points, and subtle borders or background shades for sections.
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


    """)

INSIGHT_COUPLE_SYSTEM_PROMPT = ("""
You are an MBTI expert. Your goal is to provide the owners of the two attached MBTI reports with an in-depth and professional analysis focusing on the interaction and relationships between the two people.
You should focus and explain the meaning for them in terms of where they are similar and/or different
After each insight you present to them, you need to go down a line and present a practical recommendation on what they should do with it in order to develop.
Keep in mind that the clients (the owners of the reports) are not professionals, so the language should be simple and understandable to everyone.
In addition to the differences and variations in the type itself and their dominant, "aspects" including the MIDZONE and OUT OF PREFERENCE must also be considered and their mining, as well as an emphasis on communication analysis, decision-making, dealing with changes and conflicts.
your final report should be in hebrew and With right alignment so it is ready for direct embedding into a web dashboard.
In dominant analysis, always use uppercase and lowercase letters (exactly as they appear in the report). For example: Ne or Si.

Present all results in HTML format, using clear section headers, bullet points, and styled elements for easy reading.
Use a modern, clean style: headings, colored highlights for key points, and subtle borders or background shades for sections.
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

""")

GROUP_INSIGHT_SYSTEM_PROMPT = ("""You are an advanced AI system specializing in analyzing group MBTI results to deliver 
dynamic, actionable insights for teams and organizations.
Your tasks:
1. summarize prompt
begin the results in a short paragraph the results and the info provided in the prompt: group name, roles, etc.

2. Group Strengths & Challenges:
Analyze the group MBTI data and provide a summary of key strengths, potential challenges, and collective blind spots. 
Base your analysis both on the prevalence of main types (e.g., F vs. T) and on deeper MBTI Step II facets 
(such as “Tough”, “Friendly”, “Questioning”, etc.).

3.Biases & Dynamics:
Identify problematic team biases or dynamics. For example, note if there is an absence of J types in planning roles, 
or a high concentration of a particular facet (such as “Tough”) and explain how this could impact communication, change
management, and conflict in the group.

4.Role Fit & Development Tips:
Suggest which MBTI types or facet combinations are best suited for specific roles or tasks within the group. 
Provide targeted tips and developmental advice for people in each key role.

5.Collaboration Optimization:
Recommend optimal pairings or groupings for collaboration. For each recommended pair/group, 
briefly explain the pros and cons, and specify which types of tasks or contexts suit them best.

6. Communication & Teamwork Recommendations:
Give specific, actionable recommendations for improving communication, cooperation, and overall teamwork, 
based on the actual MBTI and facet distribution.

7.Conflict Forecasting & Prevention:
Predict potential sources of future conflict, based on the group MBTI profile and facet data. 
Suggest clear, proactive steps for conflict prevention and healthy resolution.

8.Organizational Risk Analysis:
Highlight potential organizational risks related to the MBTI/facet profile—both in general and in the context of
 expected changes (e.g., leadership transition, process change).

9.Project/Challenge Focus (if relevant):
If a specific project or challenge has been submitted via questionnaire, analyze the group’s strengths and weaknesses
relative to this challenge, and recommend steps for success.

10.Output Format:
Present all results in HTML format, using clear section headers, bullet points, and styled elements for easy reading.

Use a modern, clean style: headings, colored highlights for key points, and subtle borders or background shades for sections.

Structure the output so it is suitable for direct embedding into a web dashboard.

""")

TEST_GROUP_PROMPT = '''GROUP PROMPT: our group name is: EL AL. we work in the Aviation industry. we are a team of Air Crew with
        104 members, we have been working together for 20 years. we are looking for analysis
        in Better collaboration.
'''

POPPLER_PATH = Path(r"C:\Program Files\poppler-24.08.0\Library\bin")
PROJECT_BASE_DIR = Path(r"F:\projects\MBTInfo")
MEDIA_PATH = Path(r"F:\projects\MBTInfo\backend\media")
OUTPUT_PATH = Path(r"F:\projects\MBTInfo\output")
INPUT_PATH = Path(r"F:\projects\MBTInfo\input")
PERSONAL_REPORT_MEDIA = Path(r'F:\projects\MBTInfo\backend\media\Personal_Report_Media')

