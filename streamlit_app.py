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
            title_col, button_col = st.columns([3, 1])
            if title_col.button(
                chat.name, key=f"Load {chat.id}", type="secondary"
            ):
                st.session_state.chat = chat_data.get_chat(chat.id)
            if button_col.button("🗑️", key=f"Delete {chat.id}"):
                if chat_data.delete_chat(chat.id):
                    st.session_state.chat_history = (
                        chat_data.get_chat_history()
                    )
                    st.rerun()
                else:
                    st.error("Error deleting chat.")

chat_ui.show_existing_messages()

if user_input := st.chat_input():
    chat_data.add_message("user", user_input)
    chat_ui.show_message("user", user_input)
    chat_ui.run_response_loop()
