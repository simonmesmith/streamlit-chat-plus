import streamlit as st

import chat_data
import chat_ui
from chat_data import Chat

if "chat" not in st.session_state:
    st.session_state.chat = Chat()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = chat_data.get_chat_history()

with st.sidebar:
    if st.button("New Conversation", type="primary"):
        st.session_state.chat = Chat()
    if len(st.session_state.chat_history) > 0:
        st.title("Past Chats")
        for chat in st.session_state.chat_history:
            if st.button(chat.name, key=chat.id, type="secondary"):
                st.session_state.chat = chat_data.get_chat(chat.id)

chat_ui.show_existing_messages()

if user_input := st.chat_input():
    chat_data.add_message("user", user_input)
    chat_ui.show_message("user", user_input)
    chat_ui.run_response_loop()
