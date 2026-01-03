import streamlit as st
import google.generativeai as genai
import random
import csv
import os
from datetime import datetime

# ==========================================
#  SECURE API KEY CONFIGURATION
# ==========================================
try:
    # Tries to get key from secrets file
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error(" Missing API Key!")
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
# 🎬 DATA: 10 TRAILERS (DETAILED CONTEXT & FIXED URLS)
# ==========================================
TRAILER_DB = [
    {
        "id": "batman",
        "title": "The Batman (2022)",
        "url": "https://www.youtube.com/watch?v=mqqft2x_Aa4",
        "context": """
        DETAILED VISUAL BREAKDOWN:
        - The trailer opens with the sound of duct tape tearing. A masked man (The Riddler) is standing in the dark behind a victim.
        - Commissioner Gordon lights the Bat Signal, shining it into the rainy clouds above Gotham.
        - Batman emerges from the shadows in a subway tunnel to fight a gang with painted faces.
        - Batman brutally beats a thug and says, "I'm Vengeance."
        - Bruce Wayne attends a funeral that is crashed by a car driving through the church.
        - Catwoman (Selina Kyle) is shown fighting Batman on a rooftop.
        - The Batmobile starts up with blue jet flames and chases the Penguin through fire.
        - The Riddler leaves a green greeting card and writes a question mark in a latte foam.
        - Batman leads a crowd of people through floodwaters holding a red flare.
        
        KEY OBJECTS: Duct tape, green envelope, red flare, wingsuit, heavy rain, Batmobile, makeup.
        TONE: Noir, red and black color palette, gritty, violent, Nirvana's "Something in the Way" song plays.
        """
    },
    {
        "id": "barbie",
        "title": "Barbie (2023)",
        "url": "https://www.youtube.com/watch?v=pBk4NYhWNMM",
        "context": """
        DETAILED VISUAL BREAKDOWN:
        - Panoramic shot of "Barbieland" where everything is pink plastic. Barbie floats from her roof to her car.
        - A beach scene where Ken (Ryan Gosling) asks to stay over. Barbie asks "Why?" and he says "Because we're boyfriend and girlfriend."
        - A dance party turns silent when Barbie asks, "Do you guys ever think about dying?"
        - Barbie visits "Weird Barbie" who offers a choice between a high heel (stay) and a Birkenstock sandal (truth).
        - Barbie drives her pink convertible, flies a rocket, and rides a snowmobile to get to the Real World.
        - Ken screams when a real-world police officer talks to him.
        - Barbie punches a man in the face on Venice Beach for slapping her.
        - The Mattel CEO (Will Ferrell) chases Barbie in an office building.
        
        KEY OBJECTS: Pink Corvette, rollerblades, high heels, Birkenstocks, neon outfits, Dreamhouse.
        TONE: Satirical, bright, neon colors, comedic, meta-humor, musical.
        """
    },
    {
        "id": "oppenheimer",
        "title": "Oppenheimer",
        "url": "https://www.youtube.com/watch?v=uYPbbksJxIg",
        "context": """
        DETAILED VISUAL BREAKDOWN:
        - Cillian Murphy (Oppenheimer) walks alone in a desert landscape.
        - Visuals of fire, sparks, and atoms spinning are intercut with black and white footage of men in suits.
        - General Groves (Matt Damon) and Oppenheimer discuss building a secret town (Los Alamos) in the middle of nowhere.
        - A metal sphere (the bomb gadget) is hoisted up a tower in the rain.
        - Oppenheimer puts on dark goggles.
        - A countdown sequence: "3, 2, 1" followed by a massive silent explosion of fire.
        - A map of the United States is shown with potential target markers.
        - The trailer ends with Oppenheimer saying, "I don't know if we can be trusted with such a weapon."
        
        KEY OBJECTS: Fedora hat, pipe, chalkboard equations, the "Gadget" (bomb), desert test site, marbles in a jar.
        TONE: Tense, dramatic, shifting between color and black & white, loud orchestral music.
        """
    },
    {
        "id": "avengers_endgame",
        "title": "Avengers: Endgame",
        "url": "https://www.youtube.com/watch?v=TcMBFSGVi1c",
        "context": """
        DETAILED VISUAL BREAKDOWN:
        - Tony Stark is drifting in space inside a ship, recording a goodbye message to Pepper Potts on a damaged Iron Man helmet.
        - The Marvel Studios logo turns to dust.
        - Captain America (Steve Rogers) is seen crying.
        - Bruce Banner looks at holographic screens showing "Missing" statuses for Ant-Man and Peter Parker.
        - Black Widow finds Hawkeye (Ronin) on a rainy street in Tokyo; he wipes a sword clean.
        - Black and white flashbacks show Captain America in WWII and Thor in Asgard, with only red colors highlighted.
        - The surviving Avengers walk in slow motion across a hangar wearing matching white-and-red Quantum Suits.
        - Thor summons his axe (Stormbreaker) next to Captain Marvel, who doesn't flinch.
        
        KEY OBJECTS: Damaged Iron Man helmet, Ronin sword, "Missing" posters, Quantum suits, Shield.
        TONE: Sad, somber, emotional, building up to epic determination ("Whatever it takes").
        """
    },
    {
        "id": "spiderman_nwh",
        "title": "Spider-Man: No Way Home",
        "url": "https://www.youtube.com/watch?v=JfVOs4VSpmA",
        "context": """
        DETAILED VISUAL BREAKDOWN:
        - Peter Parker and MJ lie on a rooftop reading newspapers; the world knows his identity.
        - Peter enters the Sanctum Sanctorum which is covered in snow.
        - Doctor Strange casts a spell with orange runic circles to make the world forget Peter is Spider-Man.
        - Peter interrupts the spell too many times, causing it to break and open the Multiverse.
        - Peter fights Doctor Strange on a train in the Mirror Dimension (reality bending).
        - A Green Goblin pumpkin bomb rolls onto a bridge and explodes.
        - Mechanical tentacles smash through the road. Doc Ock emerges and says, "Hello, Peter."
        
        KEY OBJECTS: Snow in the Sanctum, Spell Box, Pumpkin Bomb, Mechanical Arms, Black and Gold Suit.
        TONE: Chaotic, magical, high stakes, nostalgic villains returning.
        """
    },
    {
        "id": "top_gun",
        "title": "Top Gun: Maverick",
        "url": "https://www.youtube.com/watch?v=giXco2jaZ_4",
        "context": """
        DETAILED VISUAL BREAKDOWN:
        - An F-18 fighter jet launches off an aircraft carrier deck in golden sunlight.
        - Ed Harris tells Maverick (Tom Cruise) that his kind is headed for extinction due to drones.
        - Maverick flies a dark stealth jet at high speed over a desert.
        - Intense dogfight scenes showing pilots breathing heavily in oxygen masks.
        - A montage of pilots playing football shirtless on the beach.
        - Maverick rides his motorcycle alongside a fighter jet taking off.
        - A jet performs a "Cobra maneuver" (flips backward vertically) to dodge a missile.
        - Maverick visits a snowy funeral scene.
        
        KEY OBJECTS: F-18 Super Hornets, Aviator sunglasses, Bomber jacket, Motorcycle, Aircraft Carrier.
        TONE: Patriotic, high-octane action, golden hour lighting, intense focus, nostalgia.
        """
    },
    {
        "id": "avatar_2",
        "title": "Avatar: The Way of Water",
        "url": "https://www.youtube.com/watch?v=d9MyqF3bPhI",
        "context": """
        DETAILED VISUAL BREAKDOWN:
        - Na'vi children run through a bioluminescent jungle.
        - Jake Sully and Neytiri fly on Banshees over a massive blue ocean.
        - Underwater shots show a young Na'vi holding onto a giant alien whale (Tulkun).
        - Hyper-realistic water physics and swimming scenes.
        - A large battle scene ensues with humans in crab-like mech suits fighting Na'vi on speedboats.
        - A village built on the water burns down.
        - Jake Sully says, "This family is our fortress."
        
        KEY OBJECTS: Water, Skimwings (flying fish mounts), Bow and Arrow, Mech Suits, Braided hair, Whales.
        TONE: Visual spectacle, serene nature vs industrial war, emphasis on family protection.
        """
    },
    {
        "id": "interstellar",
        "title": "Interstellar",
        "url": "https://www.youtube.com/watch?v=zSWdZVtXT7E",
        "context": """
        DETAILED VISUAL BREAKDOWN:
        - Matthew McConaughey drives a pickup truck through a dusty cornfield chasing a drone.
        - A rocket launch sequence showing the engines igniting.
        - The spaceship (Endurance) spins rapidly in space to generate artificial gravity.
        - The crew lands on a planet covered in shallow water.
        - They realize a mountain in the distance is actually a massive tidal wave approaching them.
        - McConaughey cries while watching a video message from his grown-up daughter.
        - The ship flies near a massive glowing black hole (Gargantua).
        
        KEY OBJECTS: Cornfield, dust storm, spinning spaceship, giant wave, robot (TARS), bookshelf.
        TONE: Emotional, awe-inspiring, silent space vs loud organ music (Hans Zimmer), grand scale.
        """
    },
    {
        "id": "joker",
        "title": "Joker (2019)",
        "url": "https://www.youtube.com/watch?v=zAGVQLHvwOY",
        "context": """
        DETAILED VISUAL BREAKDOWN:
        - Arthur Fleck (Joaquin Phoenix) talks to a therapist about "negative thoughts."
        - Arthur laughs uncontrollably on a bus, making a child uncomfortable.
        - He is seen bathing his frail mother in a bathtub.
        - Arthur gets beaten up by teenagers in a dirty alleyway.
        - He dyes his hair green and applies white clown makeup in a mirror.
        - He dances triumphantly down a long concrete staircase wearing a red suit.
        - He walks onto a TV talk show set hosted by Robert De Niro, forcing a smile.
        
        KEY OBJECTS: Notebook with jokes, clown mask, gun, stairs, cigarette, yellow vest, red suit.
        TONE: Uncomfortable, psychological horror, dirty city aesthetic, slow descent into madness.
        """
    },
    {
        "id": "lion_king",
        "title": "The Lion King (2019)",
        "url": "https://www.youtube.com/watch?v=7TavVZMewpY",
        "context": """
        DETAILED VISUAL BREAKDOWN:
        - The sun rises over the African Savanna to the opening chant of "The Circle of Life."
        - Elephants, giraffes, and birds travel across the plains towards Pride Rock.
        - Rafiki (the mandrill) breaks a red root and smears the dust on Simba's forehead.
        - Baby Simba sneezes.
        - Mufasa's voiceover explains that "Everything the light touches is our kingdom."
        - A shot of the wildebeest stampede in a dark canyon.
        - Adult Simba roars on top of Pride Rock in the rain.
        - Timon and Pumbaa sing "The Lion Sleeps Tonight" while walking into the jungle.
        
        KEY OBJECTS: Pride Rock, Red root dust, paw print, beetles/grubs.
        TONE: Majestic, nostalgic, documentary-style photorealism, musical.
        """
    }
]

QUESTIONS = [
    "What was this movie trailer about?",
    "What did you like specifically in this video?",
    "What was the most memorable scene?"
]

# ==========================================
#  CSV LOGGING FUNCTION
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
#  AI LOGIC (Grammar & Context Check)
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
#  UI LOGIC
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
            st.error(f" {result['message']}")
            
        elif result['status'] == "PASS":
            st.session_state.chat_history.append(("assistant", f" {result['message']}"))
            st.session_state.retry_count = 0
            if q_index < len(QUESTIONS) - 1:
                st.session_state.step += 1
            else:
                st.session_state.step = "end"
            st.rerun()
            
        else: # FAIL
            if st.session_state.retry_count >= 2:
                st.session_state.chat_history.append(("assistant", " Moving on due to repeated errors."))
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