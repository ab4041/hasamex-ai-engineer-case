import os
from openai import OpenAI

SYSTEM = """You are an evidence-grounded research assistant for the Hasamex technical case.
Use ONLY the supplied transcript evidence. Do not add outside facts.
Do not invent statistics, motives, or conclusions.
When evidence is insufficient, say that the transcripts do not provide enough evidence.
The application separately displays exact source quotes and timestamps, so do not fabricate quotations.
Distinguish what an expert said from a general market fact.
Keep answers concise and useful for an interview-research workflow.
"""

def client():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    return OpenAI(api_key=key)

def answer(question, evidence, model=None):
    c = client()
    if c is None:
        return None
    model = model or os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
    evidence_text = "\n\n".join(
        f"[{x['market']} | {x['expert']} | {x['timestamp']} | {x['source_file']}]\n{x['text']}"
        for x in evidence
    )
    prompt = f"""Question:
{question}

Transcript evidence:
{evidence_text}

Write a concise synthesis of the evidence. Mention differences where the evidence supports them.
"""
    r = c.responses.create(
        model=model,
        instructions=SYSTEM,
        input=prompt,
    )
    return r.output_text.strip()

def themes(evidence, model=None):
    c = client()
    if c is None:
        return None
    model = model or os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
    evidence_text = "\n\n".join(
        f"[{x['market']} | {x['expert']} | {x['timestamp']}]\n{x['text']}"
        for x in evidence
    )
    prompt = f"""Analyze these three expert interviews.

Identify:
1. 4-6 common themes supported by multiple interviews.
2. 2-4 meaningful differences or tensions between interviews.
3. A short evidence-grounded synthesis.

Do not introduce outside information.

Evidence:
{evidence_text}
"""
    r = c.responses.create(model=model, instructions=SYSTEM, input=prompt)
    return r.output_text.strip()
