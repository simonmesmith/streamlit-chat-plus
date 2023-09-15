from dataclasses import dataclass, field

import streamlit as st

from config import LLM_SYSTEM_MESSAGE
from db import db_client
from llm import respond


@dataclass
class Chat:
    id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    user_email: str | None = st.experimental_user.email
    name: str | None = "New Conversation"
    messages: list[dict] | None = field(
        default_factory=lambda: [
            {"role": "system", "content": LLM_SYSTEM_MESSAGE}
        ]
    )


def get_chat_history() -> list[Chat]:
    """Get a list of past chats for the current user."""
    chats = (
        db_client()
        .table("chats")
        .select("id, name")
        .eq("user_email", st.experimental_user.email)
        .order("updated_at", desc=True)
        .execute()
    )
    return [Chat(**c) for c in chats.data] if len(chats.data) > 0 else []


def get_chat(id: int) -> Chat:
    """Get a chat from the DB."""
    chat_data = db_client().table("chats").select("*").eq("id", id).execute()
    return Chat(**chat_data.data[0]) if len(chat_data.data) > 0 else Chat()


def insert_chat(chat: Chat) -> Chat:
    """Inserts a chat into the DB."""
    chat_data = (
        db_client()
        .table("chats")
        .insert(
            {
                "user_email": chat.user_email,
                "name": chat.name,
                "messages": chat.messages,
            }
        )
        .execute()
    )
    return Chat(**chat_data.data[0])


def update_chat(chat: Chat) -> Chat:
    """Updates a chat in the DB."""
    chat_data = (
        db_client()
        .table("chats")
        .update({"messages": chat.messages})
        .eq("id", chat.id)
        .execute()
    )
    return Chat(**chat_data.data[0])


def generate_chat_name(user_message_content: str) -> str:
    """Generates a chat name based on user message content."""
    prompt = (
        "Generate a short name in title case for a conversation that "
        "starts with the following message:\n\n"
        f"{user_message_content}\n\n"
    )
    response = respond(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def add_message(
    role: str,
    content: str | None,
    function_call: dict = None,
    name: str = None,
) -> None:
    """Updates session variables and inserts into or updates DB as needed."""
    msg = {"role": role, "content": content}
    if function_call:
        msg["function_call"] = function_call
    if name:
        msg["name"] = name
    st.session_state.chat.messages.append(msg)
    # If it's the first assistant message and we haven't added the chat to the
    # chat history yet, generate a chat name, insert the chat into the DB,
    # and rerun the app to refresh the chat history. We do it this way so that
    # (1) there's no delay when the user posts their first message and (2) the
    # rerun doesn't stop subsequent activity.
    if (
        role == "assistant"
        and not function_call
        and (
            len(st.session_state.chat_history) == 0
            or st.session_state.chat_history[0].id != st.session_state.chat.id
        )
    ):
        st.session_state.chat.name = generate_chat_name(
            st.session_state.chat.messages[1]["content"]
        )
        st.session_state.chat = insert_chat(st.session_state.chat)
        st.session_state.chat_history.insert(0, st.session_state.chat)
        st.experimental_rerun()
    elif st.session_state.chat.id:  # If chat already inserted, update DB
        st.session_state.chat = update_chat(st.session_state.chat)
