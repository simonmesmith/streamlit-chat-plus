"""Streamlit entrypoint. Main chat interface."""

import streamlit as st

from chat_data import (
    Chat,
    add_message,
    delete_chat,
    get_chat,
    get_chat_history,
)
from chat_ui import run_response_loop, show_existing_messages, show_message
from config import APP_TITLE
from utils import get_base_url, get_shared_chat_id

if shared_chat_id := get_shared_chat_id():
    st.session_state.chat = get_chat(shared_chat_id)
    st.title(APP_TITLE)
    st.subheader("Shared Chat:")
    show_existing_messages()
else:
    if "chat" not in st.session_state:
        st.session_state.chat = Chat()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = get_chat_history()

    with st.sidebar:
        if st.button("New Conversation", type="primary"):
            st.session_state.chat = Chat()
        if len(st.session_state.chat_history) > 0:
            st.subheader("Past Chats")
            for chat in st.session_state.chat_history:
                title_col, button_col = st.columns([3, 1])
                if title_col.button(chat.name, key=f"Load {chat.id}"):
                    st.session_state.chat = get_chat(chat.id)
                if button_col.button("🗑️", key=f"Delete {chat.id}"):
                    if delete_chat(chat.id):
                        st.session_state.chat_history = get_chat_history()
                        st.rerun()
                    else:
                        st.error("Error deleting chat.")
                if button_col.button("🔗", key=f"Copy {chat.id}"):
                    st.toast(
                        f"{get_base_url()}?shared_chat_id={chat.id}", icon="🔗"
                    )
                st.divider()

    title_col, toggle_col = st.columns([3, 1])
    title_col.title(APP_TITLE)

    show_existing_messages()

    if user_input := st.chat_input():
        add_message("user", user_input)
        show_message("user", user_input)
        run_response_loop()
