import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("API Key not found in .env file")

genai.configure(api_key=api_key)

def validate_answer(user_answer, question, video_context, retry_count):
    """
    Analyzes the user's response.
    Returns a dictionary: {"status": "PASS" or "FAIL", "message": "Hint or Success msg"}
    """
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prompt Engineering: The instructions to the AI
    prompt = f"""
    You are an AI Evaluator for a video understanding test.
    
    CONTEXT (The Video Content): {video_context}
    QUESTION ASKED: {question}
    USER ANSWER: "{user_answer}"
    CURRENT RETRY COUNT: {retry_count} (Max is 2)

    Your Task:
    1. GIBBERISH CHECK: If the answer is random letters, too short, or meaningless -> FAIL.
    2. RELEVANCE CHECK: If the answer mentions things NOT in the context (hallucination) -> FAIL.
    3. QUALITY CHECK: If the answer is valid and makes sense -> PASS.

    Output Rules:
    - If PASS: Return exactly "PASS|Good job."
    - If FAIL: Return "FAIL|[Reason]|[Guiding Hint]"
    
    Constraints for Hint:
    - The hint must guide them to the context without giving the exact answer.
    - If this is a retry, make the hint more specific.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Parse the AI response (Expecting "STATUS|REASON|HINT")
        parts = text.split('|')
        
        if parts[0] == "PASS":
            return {"status": "PASS", "message": parts[1] if len(parts) > 1 else "Correct!"}
        else:
            # It failed
            reason = parts[1] if len(parts) > 1 else "Invalid input."
            hint = parts[2] if len(parts) > 2 else "Please try again based on the video."
            return {"status": "FAIL", "message": f"{reason} {hint}"}
            
    except Exception as e:
        # Fallback if AI fails (prevents crash)
        return {"status": "PASS", "message": "Proceeding..."}