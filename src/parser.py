from pathlib import Path
import re

TIME_RE = re.compile(r"(?m)^\s*(\d{2}:\d{2})\s*$")
HEADER_RE = re.compile(r"^([^:\n]+):\s*(.*)$")

def parse_transcript(path: str):
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()
    expert = ""
    role = ""
    market = ""
    for line in lines[:5]:
        if line.startswith("Expert"):
            expert = line.split("–", 1)[-1].strip() if "–" in line else line
        elif line.startswith("Role:"):
            role = line.split(":", 1)[1].strip()
        elif line.startswith("Market:"):
            market = line.split(":", 1)[1].strip()

    matches = list(TIME_RE.finditer(text))
    chunks = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        block = text[start:end].strip()
        if not block:
            continue
        timestamp = m.group(1)
        speaker = ""
        statement = block
        # Usually block begins "Interviewer: ..." or "Expert: ..."
        if ":" in block:
            speaker, statement = block.split(":", 1)
            speaker = speaker.strip()
            statement = statement.strip()
        chunks.append({
            "id": f"{market.lower()}_{timestamp.replace(':','')}_{len(chunks)+1}",
            "expert": expert,
            "role": role,
            "market": market,
            "timestamp": timestamp,
            "speaker": speaker,
            "text": statement,
            "source_file": Path(path).name,
        })
    return chunks

def load_all(data_dir="data"):
    paths = sorted(Path(data_dir).glob("Transcript_*.txt"))
    all_chunks = []
    for p in paths:
        all_chunks.extend(parse_transcript(str(p)))
    return all_chunks

def load_guide(path="data/Interview_Guide.txt"):
    text = Path(path).read_text(encoding="utf-8")
    questions = []
    for line in text.splitlines():
        m = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if m:
            questions.append(m.group(1).strip())
    return questions
