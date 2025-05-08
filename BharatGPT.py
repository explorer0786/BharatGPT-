import streamlit as st
from googlesearch import search
from groq import Groq
from dotenv import dotenv_values
import datetime

# Load .env variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

# Define system instructions
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Reset session state each time page refreshes
st.set_page_config(page_title="Chat with AI", layout="centered")
st.markdown("<style>footer {visibility: hidden;}</style>", unsafe_allow_html=True)

if "chat" not in st.session_state:
    st.session_state.chat = [
        {"role": "system", "content": System},
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello, how can I help you?"}
    ]

# Get Google search results
def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"
    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
    Answer += "[end]"
    return Answer

# Get real-time information
def Information():
    now = datetime.datetime.now()
    return f"""Use This Real-time Information if needed:
Day: {now.strftime('%A')}
Date: {now.strftime('%d')}
Month: {now.strftime('%B')}
Year: {now.strftime('%Y')}
Time: {now.strftime('%H')} hours, {now.strftime('%M')} minutes, {now.strftime('%S')} seconds.
"""

# AI response logic
def get_ai_response(prompt):
    st.session_state.chat.append({"role": "user", "content": prompt})
    system_context = [
        {"role": "system", "content": GoogleSearch(prompt)},
        {"role": "system", "content": Information()}
    ]
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[*st.session_state.chat, *system_context],
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True
    )

    answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content
    answer = answer.strip().replace("</s>", "")
    st.session_state.chat.append({"role": "assistant", "content": answer})
    return answer

# Styling
def render_message(role, content):
    icon = "🧑‍💻" if role == "user" else "🤖"
    color = "#f0f0f0" if role == "user" else "#fff7db"
    with st.container():
        st.markdown(
            f"""
            <div style="background-color: {color}; border-radius: 10px; padding: 15px; margin: 10px 0;">
                <strong>{icon}</strong> &nbsp; {content}
            </div>
            """,
            unsafe_allow_html=True
        )

# Chat display
st.title("💬 BharatGPT ")
for msg in st.session_state.chat:
    if msg["role"] != "system":
        render_message(msg["role"], msg["content"])

# Input form
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Ask something...", "")
    submitted = st.form_submit_button("Send")
    if submitted and user_input.strip():
        get_ai_response(user_input)
        st.experimental_rerun()
