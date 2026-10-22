"""
AI Service Main Entrypoint
"""

def analyze_text(text: str) -> dict:
    """Analyze input text and return sentiment score."""
    word_count = len(text.split())
    confidence = min(0.99, round(0.5 + (word_count * 0.05), 2))
    return {
        "text": text,
        "word_count": word_count,
        "sentiment": "positive" if word_count > 3 else "neutral",
        "confidence": confidence
    }

if __name__ == "__main__":
    sample = "Portfolio project showcasing Python AI integration"
    result = analyze_text(sample)
    print("AI Analysis Result:", result)
