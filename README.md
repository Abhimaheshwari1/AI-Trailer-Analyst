# AI Trailer Analyst

## Project Overview

AI Trailer Analyst is a conversational AI application designed to evaluate a user's comprehension of video content. The system plays specific movie trailers (e.g., The Batman, Oppenheimer) and conducts a structured interview. It utilizes **Google Gemini** (Generative AI) to validate user responses in real-time, ensuring answers are grammatically correct, logically sound, and factually relevant to the specific video context.

---

## About the Google Gemini API

This project relies on the **Google Gemini API** as its core intelligence engine.

**How it works in this application:**
1.  **Context Injection:** The application contains a "Ground Truth" database of detailed, shot-by-shot text descriptions for 10 distinct movie trailers.
2.  **Prompt Engineering:** When a user answers a question, the Python script constructs a complex prompt that combines:
    *   The detailed context of the video.
    *   The specific question asked.
    *   The user's raw answer.
    *   Strict rules for validation (Grammar, Relevance, Gibberish).
3.  **Model Inference:** This prompt is sent to Google's servers. The Gemini model (specifically the "Flash" or "Pro" variants) analyzes the logic and returns a structured "PASS" or "FAIL" verdict with feedback.
4.  **Dynamic Model Selection:** To handle Free Tier rate limits, the code automatically scans the user's account to find the best available model (prioritizing "Lite" models to prevent crashing).

---

## Features

*   **Context-Aware Validation:** The AI knows exactly what happened in the video and rejects hallucinations (e.g., mentioning aliens in a Batman movie).
*   **Gibberish Detection:** Automatically filters out random keystrokes or meaningless text.
*   **Grammar & Logic Check:** Enforces proper sentence structure and coherence.
*   **Data Logging:** All interview data (Timestamp, Movie, User Answer, AI Feedback) is automatically saved to a local CSV file named "interview_data.csv".
*   **Secure Architecture:** API keys are managed via Streamlit Secrets, ensuring they are never exposed in the code.

---

## Installation and Setup

Follow these steps to run the project locally on your machine.

### 1. Clone the Repository
Open your terminal and run:


git clone https://github.com/Abhimaheshwari1/AI-Trailer-Analyst.git
cd AI-Trailer-Analyst

2. Install Dependencies
Install the required Python libraries:

pip install -r requirements.txt
3. Configure Google API Key (CRITICAL STEP)
This application requires a Google Gemini API Key. For security reasons, the key is not included in the downloaded code. You must add your own.
Get a Key: Visit Google AI Studio (https://aistudio.google.com/) and create a free API Key.
Create the Secret Directory: Inside the main project folder, create a new folder named .streamlit (ensure there is a dot at the beginning).
Create the Config File: Inside the .streamlit folder, create a text file named secrets.toml.
Add Your Key: Open secrets.toml in Notepad (or any editor) and paste your key in this format:

GOOGLE_API_KEY = "AIzaSyD_PASTE_YOUR_REAL_KEY_HERE"
Note: Do not upload this file to GitHub. It is already ignored by the .gitignore file to keep your key safe.
How to Run
Once you have set up the secrets file, start the application by running:
streamlit run app.py
The application will launch automatically in your default web browser (usually at http://localhost:8501).
Project Structure
app.py: The main application file containing the UI, the movie database, and the AI validation logic.
requirements.txt: A list of Python libraries required to run the app.
interview_data.csv: A log file generated automatically to store user answers.
.gitignore: Configuration file that prevents sensitive files (like secrets.toml) from being uploaded to GitHub.
.streamlit/secrets.toml: (Local Only) The configuration file storing your private API key.
Troubleshooting
Error: "Missing API Key"
Ensure you created the folder .streamlit and the file secrets.toml correctly.
Ensure the variable name inside the file is exactly GOOGLE_API_KEY.
Error: "Quota limit reached" (429)
You are using the Free Tier of Google Gemini. Wait 60 seconds and try again. The application is optimized to use "Lite" models to minimize this error.
Error: "Connection Failed"
Check your internet connection.
Ensure your firewall or VPN is not blocking Google API requests.