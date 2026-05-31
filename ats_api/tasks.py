import os
import json
import pdfplumber
from celery import shared_task
import google.generativeai as genai  # ◄ Imported Google's Library
from .models import Application
from dotenv import load_dotenv
from pathlib import Path

# Explicitly load the environmental ledger variables for the Celery process
base_dir = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=os.path.join(base_dir, '.env'))

@shared_task
def process_resume(application_id):
    try:
        # Fetch target applicant payload record from your SQL ledger
        app = Application.objects.get(id=application_id)
        app.status = 'PROCESSING'
        app.save()

        # Step 1: Pull out text streams from candidate resume binary format
        text = ""
        with pdfplumber.open(app.resume.path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

        # Step 2: Configure and authenticate the Google AI Engine
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Step 3: Initialize the high-throughput, free-tier Gemini workhorse model
        model = genai.GenerativeModel("gemini-2.5-flash")

        # Step 4: Draft structural recruitment prompt rules
        prompt = f"""
        You are an expert technical recruiter matching candidate profiles to corporate descriptions.
        Analyze the candidate's resume text against the requirements provided below.
        
        Job Title: {app.job.title}
        Job Requirements: {app.job.requirements}
        
        Candidate Resume Text:
        {text}
        
        CRITICAL: You MUST respond with a valid JSON object. Do not wrap it in markdown block tags. 
        The object MUST contain exactly these keys:
        1. "score": An integer from 0 to 100 indicating match percentage.
        2. "matched_skills": A list of strings showing technical matches.
        3. "missing_skills": A list of strings showing core gaps found.
        """

        # Step 5: Execute generation request forcing strict JSON compliance
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )

        # Step 6: Parse out generated payload mapping back into database fields
        parsed_data = json.loads(response.text)

        app.ai_score = parsed_data.get("score", 0)
        app.ai_feedback = parsed_data  # Saves complete structural JSON array data
        app.status = 'REVIEWED'
        app.save()

    except Exception as e:
        # Failsafe logic to avoid process hangs on parsing drops
        if 'app' in locals():
            app.status = 'FAILED'
            app.save()
        print(f"Error processing application {application_id}: {str(e)}")