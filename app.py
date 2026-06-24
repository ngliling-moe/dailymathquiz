import random
import streamlit as st

# Set up page configuration
st.set_page_config(page_title="Math Wizards Daily Challenge", page_icon="🧮", layout="centered")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight: bold; color: #2E4053; }
    .score-box { background-color: #E8F8F5; padding: 15px; border-radius: 10px; border: 2px solid #A3E4D7; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

def init_game():
    st.session_state.score = 0
    st.session_state.question_count = 0
    st.session_state.game_over = False
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
        num2 = random.randint(10, 49) # Ensure positive result
        answer = num1 - num2
        explanation = f"Because if you take away {num2} from {num1}, you get {answer}."
    elif op == '×':
        num1 = random.randint(2, 12)
        num2 = random.randint(2, 12)
        answer = num1 * num2
        explanation = f"Because {num1} groups of {num2} is {answer}."
    else: # Division
        num2 = random.randint(2, 10)
        answer = random.randint(2, 10)
        num1 = num2 * answer # Ensure whole number results
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
    st.write("Login below to start your 5-question daily challenge!")
    
    username_input = st.text_input("Enter your Wizard Name:", max_chars=15).strip()
    
    if st.button("Enter the Math Realm ✨", type="primary"):
        if username_input:
            st.session_state.username = username_input
            st.session_state.logged_in = True
            init_game()
            st.rerun()
        else:
            st.warning("Please enter a name to play!")

# --- GAME SCREEN ---
else:
    st.title("🧮 Math Wizards Daily Challenge")
    st.write(f"Welcome back, **{st.session_state.username}**! Ready to train your brain?")
    
    # Check if 5-question limit is reached
    if st.session_state.question_count >= 5:
        st.session_state.game_over = True

    if not st.session_state.game_over:
        # Display Progress & Score
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='score-box'><b>Question:</b> {st.session_state.question_count + 1} / 5</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='score-box'><b>Current Score:</b> {st.session_state.score}⭐</div>", unsafe_allow_html=True)
        
        st.write("---")
        
        # Display Current Question
        q = st.session_state.current_question
        st.markdown(f"<p class='big-font'>What is {q['num1']} {q['op']} {q['num2']}?</p>", unsafe_allow_html=True)
        
        # Form for user answer to control submission properly
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

        # Display Feedback below the form after submission
        if st.session_state.user_answered:
            if st.session_state.is_correct:
                st.success(f"🎉 **Correct!** Great job, {st.session_state.username}! +1 Point")
            else:
                st.error(f"❌ **Not quite!** You answered {st.session_state.last_user_ans}. The correct answer was **{q['answer']}**.")
            
            st.info(f"💡 **Explanation:** {q['explanation']}")
            
            # Button to proceed to the next question
            if st.button("Next Question ➡️"):
                generate_new_question()
                st.rerun()

    # --- GAME OVER SCREEN ---
    else:
        st.balloons()
        st.markdown(f"## 🏆 Daily Challenge Complete, {st.session_state.username}!")
        st.markdown(f"### Final Score: **{st.session_state.score} / 5 stars** ⭐")
        
        if st.session_state.score == 5:
            st.success("🏅 Perfect score! You are a Grandmaster Math Wizard today!")
        elif st.session_state.score >= 3:
            st.info("👍 Great job! Keep practicing and you'll get a perfect score next time!")
        else:
            st.warning("💪 Good effort! Math is all about practice. Try again to beat your score!")

        st.write("---")
        if st.button("Play Again 🔄"):
            init_game()
            st.rerun()
            
        if st.button("Log Out 🚪", type="secondary"):
            st.session_state.logged_in = False
            st.rerun()
