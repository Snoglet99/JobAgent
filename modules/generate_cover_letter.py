from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tone_instruction = {
    "Visionary": "Speak with ambitious energy and a future-focused, transformative lens.",
    "Fixer": "Frame the candidate as a proven problem-solver who excels under pressure and uncertainty.",
    "Leader": "Emphasize authority, strategic impact, and clear ownership of outcomes.",
    "Team Player": "Highlight collaboration, emotional intelligence, and team-wide enablement.",
    "Entrepreneur": "Center on initiative, resilience, and an ability to build from zero.",
    "Default": "Use a polished, persuasive tone grounded in competence and credibility."
}

def generate_cover_letter(
    job_title,
    company,
    job_ad_text,
    job_objectives,
    cv_summary,
    resume_bullets,
    tone="Default",
    news="",
    strategy=""
):
    prompt = f"""
You are a world-class cover letter writer. Your task is to write a concise, high-impact cover letter that:

1. **Gets the applicant to the next stage**.
2. **Stays 100% truthful** — no made-up companies, numbers, or claims.
3. **Uses only the information provided — including resume, job ad, company news, and strategy context — without fabricating any experience, results, or details.**

--- CONTEXT ---
JOB TITLE: {job_title}
COMPANY: {company}

JOB OBJECTIVES (parsed from ad):
{job_objectives}

FULL JOB AD TEXT:
{job_ad_text}

CANDIDATE PROFILE SUMMARY:
{cv_summary}

RESUME BULLETS:
{resume_bullets}

RECENT COMPANY NEWS / STRATEGY:
{news}
{strategy}

TONE GUIDE: {tone_instruction.get(tone, tone_instruction['Default'])}

--- INSTRUCTIONS ---
Write the body of the cover letter (no greeting or sign-off). The letter must:

- Be **tightly aligned to the company’s objectives** using only true experience.
- **Reference quantifiable outcomes only if they appear in the resume bullets**.
- Avoid any fabricated numbers, clients, achievements, or employers.
- Be **concise, punchy, and direct** — no filler, no clichés.
- Echo the language of the job ad naturally to aid ATS matching.
- Demonstrate strategic awareness of the company’s direction (if context provided).
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a strategic, persuasive, and honest cover letter writer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
    )

    return response.choices[0].message.content.strip()
