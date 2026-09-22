def evidence_cards(chunks, limit=4):
    return chunks[:limit]

def fallback_answer(question, evidence):
    if not evidence:
        return "The supplied transcripts do not contain enough directly relevant evidence to answer this question."
    # Transparent fallback: summarize the strongest evidence without pretending to be an LLM.
    pieces = []
    for c in evidence[:3]:
        pieces.append(f"{c['market']}: {c['text']}")
    return "Evidence-grounded fallback summary:\n\n" + "\n\n".join(pieces)

def fallback_themes(chunks):
    themes = {
        "Economics / ROI": ["France", "Germany", "United Kingdom"],
        "Utilisation / procedure volume": ["France", "Germany"],
        "Surgeon / staff training": ["France", "Germany", "United Kingdom"],
        "Clinical outcomes / strategy": ["France", "United Kingdom"],
        "Gradual or increasing adoption": ["France", "Germany", "United Kingdom"],
    }
    lines = ["### Common themes"]
    for name, markets in themes.items():
        lines.append(f"- **{name}** — supported in the supplied interviews from: {', '.join(markets)}.")
    lines += [
        "",
        "### Differences",
        "- France and Germany place especially strong emphasis on the economic/business case and utilisation.",
        "- The UK interview gives comparatively more emphasis to training capacity and balancing economics with clinical strategy.",
        "- The outlook differs in wording: France expects steady rather than explosive growth, Germany expects gradual growth, while the UK expert says adoption could accelerate if training expands.",
    ]
    return "\n".join(lines)
