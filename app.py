import streamlit as st
import pandas as pd
import random
import os
from datetime import datetime

 
# Configure page
st.set_page_config(
    page_title="ESPOL - PETROTEST Competition",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
# Custom CSS styles
st.markdown("""
<style>
    .title-main {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5em;
        margin-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1em;
        margin-bottom: 30px;
    }
    .card {
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        background-color: #f0f2f6;
        margin: 10px 0;
    }
    .question-box {
        background-color: #e8f4f8;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        border-left: 5px solid #ff6b6b;
    }
    .answer-box {
        background-color: #d4edda;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        border-left: 5px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)
 
# Database file
DB_FILE = 'questions_database.csv'
 
# Initialize session
if 'current_question_idx' not in st.session_state:
    st.session_state.current_question_idx = None
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False

 
# Load data
@st.cache_data
def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        return df
    else:
        return pd.DataFrame(columns=['Number', 'Question', 'Answer', 'Area'])
 
# Save data
def save_data(df):
    df.to_csv(DB_FILE, index=False, encoding='utf-8')
 
# Function to read text
def read_text(text):
    st.info("🔈 El audio ha sido desactivado para la versión web.")
 
# Load data
df = load_data()
areas = ['Geology', 'Formation Evaluation', 'Drilling', 'Petrophysics', 'Production']
 
# HEADER
st.markdown('<div class="title-main">⛽ ESPOL - PETROTEST COMPETITION</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Study Platform - 500 Questions</div>', unsafe_allow_html=True)
st.divider()
 
# SIDEBAR - NAVIGATION
st.sidebar.title("📋 Main Menu")
option = st.sidebar.radio(
    "Select an option:",
    ["🏠 Dashboard", "➕ Add Questions", "🎲 Questions by Area", "🌀 Completely Random"]
)
 
# ====== OPTION 1: DASHBOARD ======
if option == "🏠 Dashboard":
    st.markdown("## 📊 Statistics Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Questions", len(df), delta="Available Questions")
    
    with col2:
        areas_count = df['Area'].nunique()
        st.metric("Study Areas", areas_count, delta="Topics")
    
    with col3:
        if len(df) > 0:
            questions_per_area = df['Area'].value_counts().max()
            st.metric("Max Questions/Area", questions_per_area)
    
    st.divider()
    
    # Distribution chart
    if len(df) > 0:
        st.subheader("📈 Distribution by Area")
        area_counts = df['Area'].value_counts()
        st.bar_chart(area_counts)
    else:
        st.warning("No questions yet. Start adding questions!")
 
# ====== OPTION 2: ADD QUESTIONS ======
elif option == "➕ Add Questions":
    st.markdown("## ➕ Add New Question")
    
    tab1, tab2 = st.tabs(["One by One", "Multiple (Code)"])
    
    with tab1:
        st.markdown("### Add a single question")
        
        col1, col2 = st.columns(2)
        
        with col1:
            question = st.text_area("Question:", placeholder="Enter the question here", height=100)
        
        with col2:
            answer = st.text_area("Answer:", placeholder="Enter the answer here", height=100)
        
        area = st.selectbox("Select the Area:", areas)
        
        if st.button("✅ Add Question", use_container_width=True):
            if question and answer:
                new_row = pd.DataFrame({
                    'Question': [question],
                    'Answer': [answer],
                    'Area': [area]
                })
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.success("✓ Question added successfully!")
                st.cache_data.clear()
            else:
                st.error("Please complete both the question and answer")
    
    with tab2:
        st.markdown("### Add multiple questions from code")
        st.info("💡 Paste a Python script here to add many questions at once")
        
        code_input = st.text_area(
            "Paste your Python code here:",
            value="""# Example:
# questions_to_add = [
#     {'question': 'What is...?', 'answer': 'It is...', 'area': 'Geology'},
#     {'question': 'Define...?', 'answer': 'It means...', 'area': 'Drilling'},
# ]
""",
            height=300
        )
        
        if st.button("▶️ Execute Code", use_container_width=True):
            try:
                local_vars = {}
                exec(code_input, {}, local_vars)
                
                if 'questions_to_add' in local_vars:
                    new_questions = local_vars['questions_to_add']
                    for item in new_questions:
                        new_row = pd.DataFrame({
                            'Question': [item['question']],
                            'Answer': [item['answer']],
                            'Area': [item['area']]
                        })
                        df = pd.concat([df, new_row], ignore_index=True)
                    
                    save_data(df)
                    st.success(f"✓ {len(new_questions)} questions added successfully!")
                    st.cache_data.clear()
                else:
                    st.error("Variable 'questions_to_add' not found in code")
            except Exception as e:
                st.error(f"Error executing code: {str(e)}")
 
# ====== OPTION 3: QUESTIONS BY AREA ======
elif option == "🎲 Questions by Area":
    st.markdown("## 🎲 Random Question by Area")
    
    selected_area = st.selectbox("Select an area:", areas)
    
    # Filter questions by area
    area_questions = df[df['Area'] == selected_area]
    
    if len(area_questions) == 0:
        st.warning(f"No questions found in area: {selected_area}")
    else:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("🔄 New Question", use_container_width=True):
                st.session_state.current_question_idx = random.choice(area_questions.index.tolist())
                st.session_state.show_answer = False
        
        with col2:
            st.metric("Questions in this area", len(area_questions))
        
        if st.session_state.current_question_idx is not None:
            q_data = df.loc[st.session_state.current_question_idx]
            
            st.markdown(f"**Question #{int(q_data['Number'])}**", unsafe_allow_html=True)
            
            st.markdown('<div class="question-box">', unsafe_allow_html=True)
            st.markdown("### 📝 Question:")
            st.write(q_data['Question'])
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Control buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔊 Read Question", use_container_width=True):
                    read_text(q_data['Question'])
            
            with col2:
                if st.button("💬 Show Answer", use_container_width=True):
                    st.session_state.show_answer = True
            
            with col3:
                if st.button("➡️ Next", use_container_width=True):
                    st.session_state.current_question_idx = random.choice(area_questions.index.tolist())
                    st.session_state.show_answer = False
                    st.rerun()
            
            if st.session_state.show_answer:
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown("### ✅ Answer:")
                st.write(q_data['Answer'])
                st.markdown('</div>', unsafe_allow_html=True)
                
                if st.button("🔊 Read Answer", use_container_width=True):
                    read_text(q_data['Answer'])
 
# ====== OPTION 4: COMPLETELY RANDOM ======
elif option == "🌀 Completely Random":
    st.markdown("## 🌀 Completely Random Question")
    
    if len(df) == 0:
        st.warning("No questions available")
    else:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("🎲 Random", use_container_width=True):
                st.session_state.current_question_idx = random.choice(df.index.tolist())
                st.session_state.show_answer = False
        
        with col2:
            st.metric("Total Questions", len(df))
        
        if st.session_state.current_question_idx is not None:
            q_data = df.loc[st.session_state.current_question_idx]
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**Area:** {q_data['Area']}")
            with col2:
                st.markdown(f"**Question #{int(q_data['Number'])}**")
            
            st.markdown('<div class="question-box">', unsafe_allow_html=True)
            st.markdown("### 📝 Question:")
            st.write(q_data['Question'])
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Control buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔊 Read Question", use_container_width=True):
                    read_text(q_data['Question'])
            
            with col2:
                if st.button("💬 Show Answer", use_container_width=True):
                    st.session_state.show_answer = True
            
            with col3:
                if st.button("➡️ Next", use_container_width=True):
                    st.session_state.current_question_idx = random.choice(df.index.tolist())
                    st.session_state.show_answer = False
                    st.rerun()
            
            if st.session_state.show_answer:
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown("### ✅ Answer:")
                st.write(q_data['Answer'])
                st.markdown('</div>', unsafe_allow_html=True)
                
                if st.button("🔊 Read Answer", use_container_width=True):
                    read_text(q_data['Answer'])
