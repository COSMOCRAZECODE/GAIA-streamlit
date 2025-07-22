# app.py

import streamlit as st
import pandas as pd
import webbrowser
import os
from dotenv import load_dotenv
import google.generativeai as genai
import plotly.express as px
import datetime
from PIL import Image
from carbon_calculator import calculate_carbon_footprint
from news_fetcher import get_climate_news
from agent_logic import get_dynamic_advice, summarize_news, generate_quiz, chat_with_mate
from urllib.parse import parse_qs

# Extract token from URL
query_params = st.query_params
token = query_params.get("token", None)

if token is None:
    st.error("🔒 Unauthorized. Please login through the main website.")
    st.stop()

if "news_count" not in st.session_state:
    st.session_state.news_count = 5

slogans = [
    "Small Steps, Big Impact 🌱",
    "Act Now, Save Tomorrow 🌍",
    "Be Cool, Go Green 💚",
    "Climate Action Starts With You 🔥➡️❄️",
    "Sustainable Today, Livable Tomorrow 🛤️"
]

# Set page config
st.set_page_config(page_title="Gaia: Climate Sustainability Agent", layout="wide")

st.image("assets/logo.png", width=100)

# Load logo
logo = Image.open("assets/logo.png")

# Sidebar navigation
st.sidebar.image(logo, width=120)
st.sidebar.title("Gaia")
page = st.sidebar.radio("Navigate", ["Home", "Climate News", "Carbon Calculator", "Climate Mate", "Logout"])

# Page 1: Home
if page == "Home":
    st.title("🌍 Gaia: Your Personal Climate Sustainability Agent")
    st.write("""
        Welcome to Gaia — an agentic AI-powered platform that helps you stay informed about climate change,
        calculate your carbon footprint, and take meaningful action through personalized advice and goals.
    """)
    st.markdown("---")

    index = datetime.datetime.now().timetuple().tm_yday % len(slogans)
    st.markdown(f"<h2>Today's slogan:</h2>", unsafe_allow_html=True)
    st.markdown(f"<h3>{slogans[index]},</h3>", unsafe_allow_html=True)
    st.markdown("---")

    st.header("🌱 Why Gaia?")
    st.write("""
        - Learn about real-time climate news.
        - Understand your personal environmental impact.
        - Get actionable, goal-oriented advice from our AI Agent, Gaia.
    """)

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)

    # Instantiate the model once (reuse across functions)
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

    # Chatbot UI
    st.subheader("💬 Talk to Climate Mate")
    st.write("Have a conversation about sustainable living, climate science, or green habits.")

    user_input = st.text_input("You:", placeholder="Ask something like 'How can I reduce plastic usage?'")

    # Initialize UI display history
    if "chat_display_history" not in st.session_state:
        st.session_state.chat_display_history = []

    # Initialize persistent Gemini chat session
    if "climate_mate_chat" not in st.session_state:
        st.session_state.climate_mate_chat = model.start_chat(history=[])

    # Process message
    if st.button("Send") and user_input.strip():
        try:
            convo = st.session_state.climate_mate_chat
            response = convo.send_message(user_input)

            # Update UI chat history
            st.session_state.chat_display_history.append((user_input, response.text.strip()))
            st.rerun()
        except Exception as e:
            st.error("Something went wrong in the conversation.")

    # Display the last 5 exchanges
    for user, reply in reversed(st.session_state.chat_display_history[-5:]):
        st.markdown(f"**You:** {user}")
        st.markdown(f"**Mate:** {reply}")


    # ✅ Use session state if available, else default data
    if "carbon_breakdown" in st.session_state:
        carbon_data = st.session_state.carbon_breakdown
        chart_title = "Your Latest Weekly Carbon Footprint Distribution"
    else:
        carbon_data = {
            "Transport": 2.5,
            "Electricity": 1.8,
            "Food": 1.2,
            "Waste": 0.6,
            "Others": 0.4
        }
        chart_title = "Your Default Weekly Carbon Footprint Distribution"

    df = pd.DataFrame({
        "Category": carbon_data.keys(),
        "CO₂ (tons)": carbon_data.values()
    })

    custom_colors = ["#72B5A4", "#5898A6", "#B48C9C", "#D7877F", "#CCC9A1"]

    fig = px.pie(
        df,
        names="Category",
        values="CO₂ (tons)",
        title=chart_title,
        color_discrete_sequence=custom_colors,
        hole=0.4
    )

    fig.update_traces(textinfo='percent+label', textfont_size=14)
    fig.update_layout(
        showlegend=True,
        title_font=dict(size=18),
        margin=dict(t=60, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig, use_container_width=True)

# Page 2: Climate News
elif page == "Climate News":
    
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")

    st.title("📰 Climate News")
    st.write("Fetching latest news on climate change...")
    st.markdown("<div class='section-header'>📰 Latest Climate News</div>", unsafe_allow_html=True)

    articles = get_climate_news()
    st.write(f"🧪 Total articles fetched: {len(articles)}")

    if 'summary_cache' not in st.session_state:
        st.session_state.summary_cache = {}

    for idx, article in enumerate(articles[:st.session_state.news_count]):
        st.markdown(f"### {article.get('title', 'No Title')}")
        col1, col2 = st.columns([1, 4])

        with col1:
            thumbnail = article.get("urlToImage") or "https://via.placeholder.com/100x100.png?text=No+Image"
            st.image(thumbnail, width=100)

        with col2:
            st.markdown(article.get("description", "No description available."))
            source = article.get("source", {}).get("name", "Unknown Source")
            date = article.get("publishedAt", "")[:10]
            author = article.get("author")
            st.markdown(f"📅 **Date:** {date} &nbsp;&nbsp;&nbsp;&nbsp; 🏷️ **Source:** {source} &nbsp;&nbsp;&nbsp;&nbsp;📰 **Author:** {author}")
            st.markdown(f"[🔗 Read more]({article.get('url', '#')})", unsafe_allow_html=True)

            # Summarize Button
            summary_key = f"summary_{idx}"
            if st.button(f"🧠 Summarize this article", key=f"btn_{idx}"):
                try:
                    summary_text = summarize_news(article)
                except Exception as e:
                    summary_text = f"❌ Error: {e}"
                st.session_state.summary_cache[summary_key] = summary_text

            # Show summary if available
            if summary_key in st.session_state.summary_cache:
                st.markdown("##### 📌 Gemini Summary")
                st.success(st.session_state.summary_cache[summary_key])

        st.markdown("---")

    if st.session_state.news_count < len(articles):
        if st.button("🔄 Load More News"):
            st.session_state.news_count += 5
    st.caption(f"Showing {min(st.session_state.news_count, len(articles))} of {len(articles)} articles")

# Page 3: Carbon Calculator
elif page == "Carbon Calculator":
    st.title("🧮 Personal Carbon Footprint Calculator")
    st.write("Answer the following to estimate your **weekly carbon footprint**:")

    with st.form("carbon_form"):
        st.subheader("🚗 Travel & Energy")
        km_per_week = st.number_input("Kilometers driven per week", 0, 5000, step=10)
        electricity_kwh_per_month = st.number_input("Monthly electricity usage (in kWh)", 0, 2000, step=10)
        st.divider()

        st.subheader("🍽️ Food")
        diet = st.selectbox("What best describes your diet?", ["Vegetarian", "Mixed", "Non-Vegetarian"])
        st.divider()

        st.subheader("🛩️ Flights")
        flights_per_year = st.number_input("Flights taken per year", 0, 100)

        st.subheader("♻️ Waste")
        recycles = st.radio("Do you recycle regularly?", ["Yes", "No"])

        st.subheader("🚿 Water Usage")
        water_liters_per_day = st.number_input("Average water usage per day (liters)", 0, 1000)

        st.subheader("🛍️ Shopping & Digital Usage")
        shopping_habit = st.selectbox("Shopping habit", ["Minimal", "Average", "Frequent"])
        digital_hours_per_day = st.number_input("Hours spent on internet/devices daily", 0, 24)

        submitted = st.form_submit_button("Calculate")

    if submitted:
        total, breakdown = calculate_carbon_footprint(
            km_per_week,
            electricity_kwh_per_month,
            diet,
            flights_per_year,
            recycles,
            water_liters_per_day,
            shopping_habit,
            digital_hours_per_day
        )

        st.success(f"🌍 Your estimated carbon footprint is **{total:.2f} kg CO₂ per week**.")

        # ✅ Store breakdown in session state
        st.session_state.carbon_breakdown = breakdown

        # Optional: show pie chart
        fig = px.pie(
            names=list(breakdown.keys()),
            values=list(breakdown.values()),
            title="Your Weekly Carbon Footprint Distribution",
            hole=0.4
        )
        fig.update_traces(textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

# Page 4: Climate Mate
elif page == "Climate Mate":
    st.title("🤖 Climate Mate – Your AI Sustainability Companion")
    st.write("Choose what you want to do today:")

    # --- Mode Selection Buttons ---
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🧠 Get Advice"):
            st.session_state.cm_mode = "advice"
    with col2:
        if st.button("❓ Climate Quiz"):
            st.session_state.cm_mode = "quiz"

    st.markdown("---")

    # --- 1. ADVICE MODE ---
    if st.session_state.get("cm_mode") == "advice":
        st.subheader("🧠 Gaia's Weekly Advice")
        st.write("Let Gaia suggest a weekly goal based on your footprint and progress.")
        
        footprint = st.number_input("Enter your current carbon footprint (kg CO₂/month):", 0.0, 10000.0)
        previous_goal = st.text_input("Last week's goal (if any):")
        goal_status = st.selectbox("Did you complete the goal?", ["Yes", "Partially", "No"])
        
        if st.button("Generate Advice"):
            result = get_dynamic_advice(footprint, previous_goal, goal_status)
            st.markdown("### 🤖 Gaia's Advice")
            st.info(result)

    # --- 2. QUIZ MODE ---
    elif st.session_state.get("cm_mode") == "quiz":
        st.subheader("❓ Climate Quiz")
        st.write("Test your knowledge on climate change and sustainability!")

        if "quiz_data" not in st.session_state or st.button("🧪 Generate Quiz"):
            st.session_state.quiz_data = generate_quiz()

        if st.session_state.get("quiz_data"):
            for idx, q in enumerate(st.session_state.quiz_data):
                st.markdown(f"**Q{idx+1}. {q['question']}**")
                user_answer = st.radio("Choose an option:", q["options"], key=f"quiz_q_{idx}")

                if st.button(f"Show Answer for Q{idx+1}", key=f"quiz_ans_{idx}"):
                    correct_option = q["options"][ord(q["answer"].lower()) - ord('a')]
                    st.success(f"✅ Correct Answer: {correct_option}")

                st.markdown("---")

# st.sidebar.markdown("## 🔒 Logout")
elif page == "Logout":
    webbrowser.open_new("https://gaia-flask.onrender.com/logout")
    st.stop()
