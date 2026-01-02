import streamlit as st
import google.generativeai as genai
import random
import csv
import os
from datetime import datetime

# ==========================================
# 🔑 SECURE API KEY CONFIGURATION
# ==========================================
try:
    # Tries to get key from secrets file
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("🚨 Missing API Key!")
    st.info("Please create a folder named .streamlit and a file named secrets.toml with GOOGLE_API_KEY='...'")
    st.stop()

# Configure Google AI
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

st.set_page_config(page_title="AI Video Interviewer", layout="centered")

# ==========================================
# 🎬 DATA: 10 MOVIE TRAILERS
# ==========================================
TRAILER_DB = [
    {
        "id": "batman",
        "title": "The Batman (2022)",
        "url": "https://www.youtube.com/watch?v=mqqft2x_Aa4",
        "context": "Trailer for 'The Batman'. Visuals: Dark, rainy Gotham City. Batman fights thugs in a subway. The Riddler leaves a green question mark in a latte. Explosions and Batmobile chase. Tone: Gritty, noir, violent."
    },
    {
        "id": "barbie",
        "title": "Barbie (2023)",
        "url": "https://www.youtube.com/watch?v=pBk4NYhWNMM",
        "context": "Trailer for 'Barbie'. Visuals: Pink plastic world, dreamhouse, dancing, beaches. Ken asks to stay over. They travel to the Real World (grey/corporate). Tone: Bright, colorful, comedic, musical."
    },
    {
        "id": "oppenheimer",
        "title": "Oppenheimer",
        "url": "https://www.youtube.com/watch?v=uYPbbksJxIg",
        "context": "Trailer for 'Oppenheimer'. Visuals: Cillian Murphy as a scientist. Fire, nuclear explosions, atoms spinning. Black and white scenes mixed with color. 1940s suits. Countdown to bomb test. Tone: Serious, dramatic, tense."
    },
    {
        "id": "avengers_endgame",
        "title": "Avengers: Endgame",
        "url": "https://www.youtube.com/watch?v=TcMBFSGVi1c",
        "context": "Trailer for Avengers Endgame. Visuals: Tony Stark drifting in space. Captain America crying. The Avengers walking in red and white suits. Flashbacks to previous movies using black and white. Tone: Sad, epic, finality."
    },
    {
        "id": "spiderman_nwh",
        "title": "Spider-Man: No Way Home",
        "url": "https://www.youtube.com/watch?v=JfVOs4VSpmA",
        "context": "Trailer for Spider-Man No Way Home. Visuals: Peter Parker asks Dr. Strange for a spell. The spell goes wrong. Doc Ock appears with mechanical arms. Green Goblin laughs. Multiverse opening. Tone: Action, magical, chaotic."
    },
    {
        "id": "top_gun",
        "title": "Top Gun: Maverick",
        "url": "https://www.youtube.com/watch?v=giXco2jaZ_4",
        "context": "Trailer for Top Gun Maverick. Visuals: Tom Cruise flying fighter jets. Dogfights in the air. Aircraft carriers. Beach volleyball scene. Tom Cruise riding a motorcycle. Tone: Adrenaline, action, patriotic."
    },
    {
        "id": "avatar_2",
        "title": "Avatar: The Way of Water",
        "url": "https://www.youtube.com/watch?v=d9MyqF3bPhI",
        "context": "Trailer for Avatar 2. Visuals: Blue aliens (Na'vi) swimming underwater. Giant whales and sea creatures. Flying on dragon-like creatures over the ocean. Beautiful 3D landscapes. Tone: Visual spectacle, nature, family."
    },
    {
        "id": "interstellar",
        "title": "Interstellar",
        "url": "https://www.youtube.com/watch?v=zSWdZVtXT7E",
        "context": "Trailer for Interstellar. Visuals: Matthew McConaughey driving in cornfields. Rocket launch. Spaceship spinning in space. Giant water wave on a planet. Wormhole. Tone: Sci-fi, emotional, mysterious, epic."
    },
    {
        "id": "joker",
        "title": "Joker (2019)",
        "url": "https://www.youtube.com/watch?v=zAGVQLHvwOY",
        "context": "Trailer for Joker. Visuals: Arthur Fleck laughing uncontrollably on a bus. Putting on clown makeup. Dancing on stairs. Gotham looks dirty and chaotic. Robert De Niro as a talk show host. Tone: Psychological thriller, disturbing, dark."
    },
    {
        "id": "lion_king",
        "title": "The Lion King (2019)",
        "url": "https://www.youtube.com/watch?v=7TavVZMewpY",
        "context": "Trailer for The Lion King (CGI). Visuals: African savanna. Baby Simba being lifted on Pride Rock. Wildebeest stampede. Mufasa talking to Simba. Scar looking evil. Tone: Majestic, nostalgic, realistic animation."
    }
]

QUESTIONS = [
    "What was this movie trailer about?",
    "What did you like specifically in this video?",
    "What was the most memorable scene?"
]

# ==========================================
# 💾 CSV LOGGING FUNCTION
# ==========================================
CSV_FILE_PATH = 'interview_data.csv'

def log_to_csv(data_row):
    """Appends a row of data to the CSV file."""
    # Check if file exists to see if headers are needed
    file_exists = os.path.exists(CSV_FILE_PATH)
    
    with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            # Write Header
            writer.writerow(["Timestamp", "Trailer Title", "Question", "User Answer", "Status", "AI Feedback"])
        # Write Data
        writer.writerow(data_row)

# ==========================================
# 🧠 AI LOGIC (Grammar & Context Check)
# ==========================================
def validate_answer(user_answer, question, video_context, retry_count):
    
    # 1. AUTO-DETECT MODEL
    target_model_name = None
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini' in m.name:
                    target_model_name = m.name
                    break 
        if not target_model_name:
            return {"status": "ERROR", "message": "No valid Gemini models found."}
        model = genai.GenerativeModel(target_model_name)
    except Exception as e:
        return {"status": "ERROR", "message": f"Connection Failed: {e}"}

    # 2. PROMPT ENGINEERING
    prompt = f"""
    You are an AI Evaluator for a video comprehension test.
    
    CONTEXT (Video Content): {video_context}
    QUESTION: {question}
    USER ANSWER: "{user_answer}"
    
    Your Task is to validate the answer based on these STRICT rules:
    
    1. GRAMMAR CHECK: 
       - If the sentence makes no sense or has broken grammar (e.g., "Movie see good I like"), return FAIL.
       - The user must write a coherent sentence.
       
    2. GIBBERISH CHECK: 
       - If the input is random keys (e.g., "asdf", "lol"), return FAIL.
       
    3. RELEVANCE CHECK: 
       - The answer MUST relate to the Context provided. 
       - If they mention things not in the video (e.g., "I liked the aliens" when watching Batman), return FAIL.

    Output Format (Select one):
    - PASS|Good job.
    - FAIL|Grammar Error|Your sentence is grammatically incorrect. Please write a proper sentence.
    - FAIL|Gibberish|Please type a meaningful answer.
    - FAIL|Irrelevant|That doesn't match the video content.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        parts = text.split('|')
        
        if parts[0] == "PASS":
            return {"status": "PASS", "message": parts[1] if len(parts) > 1 else "Correct!"}
        else:
            reason = parts[1] if len(parts) > 1 else "Invalid input."
            hint = parts[2] if len(parts) > 2 else "Please try again."
            return {"status": "FAIL", "message": f"{reason} {hint}"}
            
    except Exception as e:
        return {"status": "ERROR", "message": f"API Error: {str(e)}"}

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
    st.write("Click below to watch a random movie trailer.")
    if st.button("Start Assignment"):
        st.session_state.selected_trailer = random.choice(TRAILER_DB)
        st.session_state.step = "playing"
        st.rerun()

# STEP 2: VIDEO
elif st.session_state.step == "playing":
    trailer = st.session_state.selected_trailer
    st.subheader(f"Watching: {trailer['title']}")
    st.video(trailer['url'])
    st.info("Watch carefully. You will be tested on the content.")
    
    if st.button("I have finished watching"):
        st.session_state.step = 0
        st.rerun()

# STEP 3: QUESTIONS
elif isinstance(st.session_state.step, int):
    q_index = st.session_state.step
    current_q = QUESTIONS[q_index]
    trailer_context = st.session_state.selected_trailer['context']
    
    for role, text in st.session_state.chat_history:
        with st.chat_message(role):
            st.write(text)
            
    with st.chat_message("assistant"):
        st.write(f"**Question {q_index + 1}:** {current_q}")
        
    user_input = st.chat_input("Type your answer here...")
    
    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        
        with st.spinner("AI is analyzing grammar and logic..."):
            result = validate_answer(user_input, current_q, trailer_context, st.session_state.retry_count)
        
        # --- SAVE TO CSV ---
        log_data = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            st.session_state.selected_trailer['title'],
            current_q,
            user_input,
            result['status'],
            result['message']
        ]
        log_to_csv(log_data)
        # -------------------

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
    st.success("Assignment Complete!")
    st.info(f"Data saved to {CSV_FILE_PATH}")
    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()