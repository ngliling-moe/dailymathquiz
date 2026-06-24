import os
import random
import pandas as pd
import streamlit as st

# Set up page configuration
st.set_page_config(page_title="Math Wizards Academy", page_icon="🧮", layout="centered")

# --- DATABASE SETUP (CSV) ---
# A simple CSV file to track cumulative user progress
CSV_FILE = "student_scores.csv"

def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        # Create a new dataframe if it doesn't exist yet
        return pd.DataFrame(columns=["Username", "Role", "Total_Score", "Games_Played"])

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# Load database into memory
db = load_data()

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .big-font { font-size:26px !important; font-weight: bold; color: #2E4053; }
    .score-box { background-color: #E8F8F5; padding: 15px; border-radius: 10px; border: 2px solid #A3E4D7; text-align: center; }
    .admin-box { background-color: #FEF9E7; padding: 15px; border-radius: 10px; border: 2px solid #F9E79F; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = "Student"

def init_game():
    st.session_state.score = 0
    st.session_state.question_count = 0
    st.session_state.game_over = False
    st.session_state.saved_to_db = False
    generate_new_question()

def generate_new_question():
    ops = ['+', '-', '×', '÷']
    op = random.choice(ops)
    
    if op == '+':
        num1 = random.randint(10, 99)
        num2 = random.randint(10, 99)
        answer = num1 + num2
        explanation = f"Because {num1} + {num2} equals {answer}."
    elif op == '-':
        num1 = random.randint(50, 99)
        num2 = random.randint(10, 49)
        answer = num1 - num2
        explanation = f"Because if you start with {num1} and take away {num2}, you have {answer} left."
    elif op == '×':
        num1 = random.randint(2, 12)
        num2 = random.randint(2, 12)
        answer = num1 * num2
        explanation = f"Because {num1} groups of {num2} makes {answer}."
    else: # Division
        num2 = random.randint(2, 10)
        answer = random.randint(2, 10)
        num1 = num2 * answer
        explanation = f"Because {num2} goes into {num1} exactly {answer} times (since {num2} × {answer} = {num1})."

    st.session_state.current_question = {
        "num1": num1,
        "num2": num2,
        "op": op,
        "answer": answer,
        "explanation": explanation
    }
    st.session_state.user_answered = False

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.title("🧙‍♂️ Welcome to Math Wizards!")
    st.write("Log in to practice your daily 5 questions and earn stars!")
    
    username_input = st.text_input("Enter your Name:", max_chars=15).strip()
    
    # Secret way to sign in as the teacher/monitor
    is_teacher = st.checkbox("I am the Teacher / Monitor")
    password = ""
    if is_teacher:
        password = st.text_input("Enter Teacher Password:", type="password")

    if st.button("Enter the Math Realm ✨", type="primary"):
        if username_input:
            if is_teacher and password != "mathisawesome": # Change this password to whatever you like!
                st.error("Incorrect Teacher Password!")
            else:
                st.session_state.username = username_input
                st.session_state.role = "Teacher" if is_teacher else "Student"
                st.session_state.logged_in = True
                
                # Register user in database if they don't exist yet
                if username_input not in db["Username"].values:
                    new_user = pd.DataFrame([{"Username": username_input, "Role": st.session_state.role, "Total_Score": 0, "Games_Played": 0}])
                    db = pd.concat([db, new_user], ignore_index=True)
                    save_data(db)
                
                init_game()
                st.rerun()
        else:
            st.warning("Please enter a name to play!")

# --- TEACHER / MONITOR DASHBOARD ---
elif st.session_state.role == "Teacher":
    st.title("📊 Teacher Monitoring Dashboard")
    st.write(f"Hello, **{st.session_state.username}**. Here is how your students are doing:")
    
    # Filter out teachers from the leaderboard view if wanted
    student_db = db[db["Role"] == "Student"]
    
    if not student_db.empty:
        st.markdown("### 🏆 Student Leaderboard (Accumulated Points)")
        # Sort by highest score
        sorted_db = student_db.sort_values(by="Total_Score", ascending=False).reset_index(drop=True)
        st.dataframe(sorted_db[["Username", "Total_Score", "Games_Played"]], use_container_width=True)
    else:
        st.info("No students have logged in or played yet.")
        
    st.write("---")
    if st.button("Log Out 🚪", type="secondary"):
        st.session_state.logged_in = False
        st.rerun()

# --- STUDENT GAME SCREEN ---
else:
    st.title("🧮 Math Wizards Daily Challenge")
    st.write(f"Welcome back, **{st.session_state.username}**! Ready to train your brain?")
    
    # Fetch historical stats for motivation
    user_stats = db[db["Username"] == st.session_state.username].iloc[0]
    st.sidebar.markdown(f"### 🎖️ Your Stats\n* **Total Points:** {user_stats['Total_Score']} ⭐\n* **Days Played:** {user_stats['Games_Played']} 📅")

    if st.session_state.question_count >= 5:
        st.session_state.game_over = True

    if not st.session_state.game_over:
        # Display Progress & Score
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='score-box'><b>Question:</b> {st.session_state.question_count + 1} / 5</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='score-box'><b>Current Score:</b> {st.session_state.score} ⭐</div>", unsafe_allow_html=True)
        
        st.write("---")
        
        # Display Question
        q = st.session_state.current_question
        st.markdown(f"<p class='big-font'>What is {q['num1']} {q['op']} {q['num2']}?</p>", unsafe_allow_html=True)
        
        with st.form(key="question_form", clear_on_submit=True):
            user_ans = st.number_input("Your Answer:", step=1, value=None, placeholder="Type your answer here...")
            submit_btn = st.form_submit_button("Submit Answer", type="primary")
            
            if submit_btn:
                if user_ans is not None:
                    st.session_state.user_answered = True
                    st.session_state.last_user_ans = user_ans
                    st.session_state.question_count += 1
                    
                    if user_ans == q['answer']:
                        st.session_state.score += 1
                        st.session_state.is_correct = True
                    else:
                        st.session_state.is_correct = False
                else:
                    st.warning("Please type an answer before clicking submit!")

        if st.session_state.user_answered:
            if st.session_state.is_correct:
                st.success(f"🎉 **Correct!** Great job! +1 Point")
            else:
                st.error(f"❌ **Not quite!** You answered {st.session_state.last_user_ans}. The correct answer was **{q['answer']}**.")
            
            st.info(f"💡 **Explanation:** {q['explanation']}")
            
            if st.button("Next Question ➡️"):
                generate_new_question()
                st.rerun()

    # --- GAME OVER / SAVE SCORE ---
    else:
        # Save score to local CSV file just once upon game completion
        if not st.session_state.saved_to_db:
            db.loc[db["Username"] == st.session_state.username, "Total_Score"] += st.session_state.score
            db.loc[db["Username"] == st.session_state.username, "Games_Played"] += 1
            save_data(db)
            st.session_state.saved_to_db = True

        st.balloons()
        st.markdown(f"## 🏆 Daily Challenge Complete, {st.session_state.username}!")
        st.markdown(f"### Today's Score: **{st.session_state.score} / 5 stars** ⭐")
        
        if st.session_state.score == 5:
            st.success("🏅 Perfect score! You are a Grandmaster Math Wizard today!")
        elif st.session_state.score >= 3:
            st.info("👍 Great job! Your points have been added to your total score!")
        else:
            st.warning("💪 Good effort! Every challenge makes you smarter. Try again tomorrow!")

        st.write("---")
        col_retry, col_logout = st.columns(2)
        with col_retry:
            if st.button("Play Again 🔄", use_container_width=True):
                init_game()
                st.rerun()
        with col_logout:
            if st.button("Log Out 🚪", type="secondary", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()
