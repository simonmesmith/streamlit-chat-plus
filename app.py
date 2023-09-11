import streamlit as st

import chat_manager

st.title("LitSense Chatbot")

chat_manager.show_existing_messages()


if user_input := st.chat_input():
    chat_manager.add_message("user", user_input)
    chat_manager.show_message("user", user_input)
    chat_manager.run_response_loop()
