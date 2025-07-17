import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Instantiate the model once (reuse across functions)
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

### --- Existing Advisor Logic --- ###
def generate_goals(footprint):
    if footprint > 1000:
        return "Reduce electricity usage by 10% and car travel by 20% this week."
    elif footprint > 700:
        return "Try switching 3 meat meals to vegetarian and take public transport twice."
    elif footprint > 500:
        return "Walk or cycle 3 days this week instead of driving."
    else:
        return "You're doing great! Maintain your current habits and plant a tree 🌱"

def get_advice(progress):
    if progress == "Yes":
        return "Awesome job! You're on your way to becoming a climate hero! 🌍"
    elif progress == "Partially":
        return "Nice effort! Let’s go full-on next week — you’ve got this!"
    elif progress == "No":
        return "That’s okay. Small steps matter. Let’s restart stronger 💪"
    else:
        return "Keep up the climate action!"

def get_dynamic_advice(footprint, previous_goal, goal_status):
    try:
        prompt = f"""
        The user has a carbon footprint of {footprint} kg CO₂/month.
        Last week's goal was: '{previous_goal}', and the user {goal_status.lower()} achieved it.
        Based on this, suggest a new, realistic weekly climate goal and one motivational message.

        Format:
        Goal: ...
        Advice: ...
        """
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print("Gemini failed, using fallback logic:", e)
        return f"Goal: {generate_goals(footprint)}\nAdvice: {get_advice(goal_status)}"

### --- News Summarizer --- ###
def summarize_news(article):
    try:
        prompt = f"""
        Summarize the following climate news article in 2-3 bullet points:

        Title: {article.get("title", "No Title")}

        Description: {article.get("description", "No description available.")}
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Error generating summary: {e}"

### --- New Feature 2: Quiz Generator --- ###
def generate_quiz():
    try:
        prompt = """
        Create 5 multiple-choice questions (MCQs) related to climate change and sustainability.
        Format:
        Q: Question text?
        a) Option A
        b) Option B
        c) Option C
        d) Option D
        Answer: <correct_option_letter>
        """

        response = model.generate_content(prompt)
        raw = response.text.strip()
        questions = []
        for block in raw.split("Q: ")[1:]:
            lines = block.strip().splitlines()
            q = lines[0].strip()
            options = [l.strip() for l in lines[1:5]]
            answer_line = lines[5].strip() if len(lines) > 5 else ""
            answer = answer_line.split(":")[-1].strip().lower()
            questions.append({
                "question": q,
                "options": options,
                "answer": answer
            })
        return questions
    except Exception as e:
        print("Failed to generate quiz:", e)
        return []

def chat_with_mate(chat_history_gemini, user_input):
    try:
        if not chat_history_gemini:
            chat_history_gemini = []

        convo = model.start_chat(history=chat_history_gemini)
        response = convo.send_message(user_input)

        chat_history_gemini.append({"role": "user", "parts": [user_input]})
        chat_history_gemini.append({"role": "model", "parts": [response.text]})

        return response.text.strip(), chat_history_gemini
    except Exception as e:
        return "Something went wrong in the conversation.", chat_history_gemini
