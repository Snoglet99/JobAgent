from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_cover_letter(job_title, company, job_ad_text, job_objectives, profile, news="", strategy="", tone="Default"):
    tone_instruction = {
        "Visionary": "Speak with ambitious energy and a future-focused, transformative lens.",
        "Fixer": "Frame the candidate as a proven problem-solver who excels under pressure and uncertainty.",
        "Leader": "Emphasize authority, strategic impact, and clear ownership of outcomes.",
        "Team Player": "Highlight collaboration, emotional intelligence, and team-wide enablement.",
        "Entrepreneur": "Center on initiative, resilience, and an ability to build from zero.",
        "Default": "Use a polished, persuasive tone grounded in competence and credibility."
    }

    prompt = f"""
You are a world-class cover letter writer who optimizes for two outcomes:

1. The applicant is invited to the next stage.
2. The letter is truthful and aligned to the applicant’s actual strengths.

--- CONTEXT ---
JOB TITLE: {job_title}
COMPANY: {company}

JOB OBJECTIVES (parsed from ad):
{job_objectives}

JOB AD TEXT:
{job_ad_text}

CANDIDATE PROFILE SUMMARY:
{profile.get('cv_summary', '')}

RESUME BULLETS:
{profile.get('resume_bullets', '')}

STRATEGIC CONTEXT (recent news, vision, or media):
{news}
{strategy}

TONE GUIDE: {tone_instruction.get(tone, tone_instruction['Default'])}

--- INSTRUCTIONS ---
Write a concise, persuasive cover letter that:

- **Directly addresses the company’s stated objectives** using the applicant’s real achievements.
- **Leads with quantifiable results** from the resume (e.g. cost savings, growth, efficiency).
- **Avoids fluff** — no clichés, no long intros, no vague praise.
- **Uses relevant job ad phrasing** naturally to improve ATS pass-through.
- **Reflects the company’s strategic direction** (from media/news) to show insight.
- **Never exaggerates or fabricates** skills. Stay true to the provided resume bullets and summary.

Do not include greetings or sign-offs. Output only the body of the cover letter.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a world-class job application writer. Be strategic, persuasive, and honest."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.65
    )

    return response.choices[0].message.content.strip()
