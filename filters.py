import re
from config import KEYWORDS, MIN_RELEVANCE_SCORE

def normalize(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def classify(text):
    text = normalize(text)
    categories = []
    for category, words in KEYWORDS.items():
        if any(word.lower() in text for word in words):
            categories.append(category)
    return categories

def relevance_score(text):
    text = normalize(text)
    score = 0
    for words in KEYWORDS.values():
        if any(word.lower() in text for word in words):
            score += 5
    for word in ["sardegna", "autotrasporto", "artigiano", "trasporto merci"]:
        if word in text:
            score += 10
    return score

def is_relevant(text):
    return relevance_score(text) >= MIN_RELEVANCE_SCORE

def analyze(text):
    score = relevance_score(text)
    return {"score": score, "relevant": score >= MIN_RELEVANCE_SCORE, "categories": classify(text)}
