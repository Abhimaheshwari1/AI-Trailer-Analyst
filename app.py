import streamlit as st
import google.generativeai as genai
import os
import random

# ==========================================
# 🔑 API KEY CONFIGURATION
# ==========================================
# 👇 PASTE YOUR KEY HERE
GOOGLE_API_KEY = "AIzaSyBuGCjmaoiWfpE35c9YqQkYFZAs-ISJlZI"

# Validate Key
if "PASTE_YOUR" in GOOGLE_API_KEY:
    st.error("🚨 STOP: You must paste your API Key in line 11 of app.py")
    st.stop()

# Configure
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

st.set_page_config(page_title="AI Video Interviewer", layout="centered")

# ==========================================
# 🎬 DATA
# ==========================================
TRAILER_DB = [
    {
        "id": "batman",
        "title": "The Batman (2022)",
        "url": "https://www.youtube.com/watch?v=mqqft2x_Aa4",
        "context": "The video is a trailer for 'The Batman'. Visuals: Dark, rainy Gotham City. Batman fights thugs in a subway. The Riddler leaves a green question mark. Explosions and Batmobile chase. Tone: Gritty, noir, violent."
    },
    {
        "id": "barbie",
        "title": "Barbie (2023)",
        "url": "https://www.youtube.com/watch?v=pBk4NYhWNMM",
        "context": "The video is a trailer for 'Barbie'. Visuals: Pink plastic world, dreamhouse, dancing, beaches. Ken asks to stay over. They go to the Real World. Tone: Bright, colorful, comedic."
    }
]

QUESTIONS = [
    "What was this movie trailer about?",
    "What did you like specifically in this video?",
    "What was the most memorable scene?"
]

# ==========================================
# 🧠 AI LOGIC (AUTO-DETECT MODEL)
# ==========================================
def validate_answer(user_answer, question, video_context, retry_count):
    
    # 🔴 MAGIC FIX: Find a model that actually works for you
    target_model_name = None
    try:
        # Ask Google: "What models do I have access to?"
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini' in m.name:
                    target_model_name = m.name
                    break # We found one! Stop looking.
        
        if not target_model_name:
            return {"status": "ERROR", "message": "No valid Gemini models found for this API key."}
            
        # Use the model we found (e.g., 'models/gemini-1.5-flash-001')
        model = genai.GenerativeModel(target_model_name)
    
    except Exception as e:
        return {"status": "ERROR", "message": f"Connection Failed: {e}"}

    # ----------------------------------------
    # Standard Prompt Logic
    # ----------------------------------------
    prompt = f"""
    You are an AI Evaluator.
    Context: {video_context}
    Question: {question}
    User Answer: "{user_answer}"
    
    Rules:
    - If answer is gibberish/random keys -> FAIL|Gibberish|Please use real words.
    - If answer is unrelated to context -> FAIL|Irrelevant|That wasn't in the video.
    - If answer is valid -> PASS|Good point.

    Return ONLY: PASS|Message OR FAIL|Reason|Hint
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        parts = text.split('|')
        
        if parts[0] == "PASS":
            return {"status": "PASS", "message": parts[1] if len(parts) > 1 else "Correct!"}
        else:
            reason = parts[1] if len(parts) > 1 else "Invalid input."
            hint = parts[2] if len(parts) > 2 else "Try describing the visual scenes."
            return {"status": "FAIL", "message": f"{reason} {hint}"}
            
    except Exception as e:
        return {"status": "ERROR", "message": f"API Error ({target_model_name}): {str(e)}"}

# ==========================================
# 🖥️ UI LOGIC
# ==========================================
if 'step' not in st.session_state:
    st.session_state.step = "start"
if 'selected_trailer' not in st.session_state:
    st.session_state.selected_trailer = None
if 'retry_count' not in st.session_state:
    st.session_state.retry_count = 0
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

st.title("🎬 AI Trailer Analyst")

# STEP 1: START
if st.session_state.step == "start":
    st.write("Click below to start.")
    if st.button("Start Assignment"):
        st.session_state.selected_trailer = random.choice(TRAILER_DB)
        st.session_state.step = "playing"
        st.rerun()

# STEP 2: VIDEO
elif st.session_state.step == "playing":
    trailer = st.session_state.selected_trailer
    st.subheader(f"Watching: {trailer['title']}")
    st.video(trailer['url'])
    if st.button("I have finished watching"):
        st.session_state.step = 0
        st.rerun()

# STEP 3: QUESTIONS
elif isinstance(st.session_state.step, int):
    q_index = st.session_state.step
    current_q = QUESTIONS[q_index]
    trailer_context = st.session_state.selected_trailer['context']
    
    # History
    for role, text in st.session_state.chat_history:
        with st.chat_message(role):
            st.write(text)
            
    # Question
    with st.chat_message("assistant"):
        st.write(f"**Question {q_index + 1}:** {current_q}")
        
    user_input = st.chat_input("Type your answer here...")
    
    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        
        with st.spinner("AI is finding a model and analyzing..."):
            result = validate_answer(user_input, current_q, trailer_context, st.session_state.retry_count)
        
        if result['status'] == "ERROR":
            st.error(f"❌ {result['message']}")
            
        elif result['status'] == "PASS":
            st.session_state.chat_history.append(("assistant", f"✅ {result['message']}"))
            st.session_state.retry_count = 0
            if q_index < len(QUESTIONS) - 1:
                st.session_state.step += 1
            else:
                st.session_state.step = "end"
            st.rerun()
            
        else: # FAIL
            if st.session_state.retry_count >= 2:
                st.session_state.chat_history.append(("assistant", "❌ Moving on due to repeated errors."))
                st.session_state.retry_count = 0
                if q_index < len(QUESTIONS) - 1:
                    st.session_state.step += 1
                else:
                    st.session_state.step = "end"
            else:
                st.session_state.retry_count += 1
                st.session_state.chat_history.append(("assistant", f"⚠️ {result['message']}"))
            st.rerun()

elif st.session_state.step == "end":
    st.success("Interview Complete!")
    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()