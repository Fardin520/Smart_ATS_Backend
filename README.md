# Smart ATS Backend 

Hey there! Welcome to the backend engine of my AI-Powered Applicant Tracking System (ATS). 

I built this project because standard recruitment tools are slow and often require recruiters to manually open hundreds of resume PDFs. This backend automates the heavy lifting. It takes a resume file, extracts the text, passes it to Google Gemini AI to judge how well the candidate fits the job, and calculates a live leaderboard—all without breaking a sweat or slowing down the user experience.

---

##  What Makes This Project Special?

If you look at the code, you'll see it's not just a basic Django script. I designed this as a **decoupled, distributed system**. 

When a recruiter uploads a resume, the API doesn't make them sit around waiting for the AI to process it. Instead, the backend immediately hands back a `201 Created` receipt. Out of sight, a background worker takes over the heavy lifting. This keeps the API lightning fast and incredibly responsive.

Here is what it does under the hood:
* **Smart PDF Parsing:** It reads raw, multi-page binary PDF uploads and extracts the text cleanly.
* **Cognitive AI Analysis:** It sends that text to Google Gemini 2.5 Flash, returning structured data (matched skills, missing skills, and a hiring verdict) instead of messy text blocks.
* **Automated Email Alerts:** The exact millisecond the AI finishes scoring a resume, the system automatically triggers a background email notification to the candidate.
* **Dynamic Leaderboards:** It uses database queries to mathematically sort all applicants from highest match score to lowest match score on the fly.

---

##  The Core Tech Stack

* **The Framework:** Django & Django REST Framework (Building the REST API)
* **The Brains:** Google Gemini 2.5 Flash API (Handling the resume evaluation)
* **The Heavy Lifter:** Celery (Running the background tasks)
* **The Messenger:** Redis (Acting as the message broker between Django and Celery)
* **The Database:** SQLite (Storing jobs and candidate data)
* **The Wrapper:** Docker & Docker Compose (Packaging everything so it runs anywhere)

---

##  How to Run It (The Easy Way)

Because this system uses multiple moving parts (Django, a Redis mailbox, and a Celery worker), manually configuring it on your local machine can be a headache. To fix that, I fully **Dockerized** the entire ecosystem. 

You don't need Python, Redis, or virtual environments installed on your machine. You only need **Docker Desktop**.

### 1. Set Up Your Environment Keys
Create a file named `.env` in the root folder of the project and drop your Google AI studio key inside:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
