"""Chat UI functions for the Streamlit interface."""

from typing import Literal

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

import chat_data
from llm import respond
from llm_functions import call_function, functions


def show_existing_messages() -> None:
    """Shows existing messages."""
    for msg in st.session_state.chat.messages:
        if msg["role"] in ["user", "assistant"] and msg["content"]:
            show_message(msg["role"], msg["content"])
        elif msg["role"] == "function":
            show_message(msg["role"], msg["content"], name=msg["name"])


def show_message(
    role: str,
    content: str,
    content_placeholder: DeltaGenerator | None = None,
    name: str | None = None,
    state: Literal["running", "complete", "error"] = "complete",
) -> None:
    """Shows a message."""
    if role == "function":
        content_placeholder = show_function_message(
            content, content_placeholder, name, state
        )
    elif role == "assistant":
        content_placeholder = show_assistant_message(
            content, content_placeholder
        )
    elif role == "user":
        content_placeholder = show_user_message(content, content_placeholder)
    else:
        raise ValueError(f"Invalid role: {role}")
    return content_placeholder


def show_function_message(
    content: str | None = None,
    content_placeholder: DeltaGenerator | None = None,
    name: str | None = "function",
    state: Literal["running", "complete", "error"] = "complete",
) -> DeltaGenerator:
    """Shows a function message."""

    if not content_placeholder:
        content_placeholder = st.status(label=name, state=state)
    if state == "complete":
        content_placeholder.update(state=state)
        with content_placeholder:
            # Streamlit markdown ignores \n. Mainly an issue with function
            # content containing \n. So just adding this here right now:
            content = content.replace("\n", "<br/>") if content else None
            st.markdown(content, unsafe_allow_html=True)

    return content_placeholder


def show_assistant_message(
    content: str | None, content_placeholder: DeltaGenerator | None
) -> DeltaGenerator:
    """Shows an assistant message."""
    if not content_placeholder:
        with st.chat_message("assistant"):
            content_placeholder = st.empty()
    content_placeholder.markdown(content)
    return content_placeholder


def show_user_message(
    content: str | None, content_placeholder: DeltaGenerator | None
) -> DeltaGenerator:
    """Shows a user message."""
    if not content_placeholder:
        with st.chat_message("user"):
            content_placeholder = st.empty()
    content_placeholder.markdown(content)
    return content_placeholder


def run_response_loop():
    """Runs the response loop."""
    assistant_responded = False
    while not assistant_responded:
        assistant_content = ""
        assistant_content_placeholder = None
        function_call = {"name": "", "arguments": ""}
        function_content_placeholder = None

        response = respond(
            model="gpt-4",
            functions=functions,
            messages=st.session_state.chat.messages,
            stream=True,
        )

        for chunk in response:
            choice = chunk["choices"][0]
            if "delta" in choice and "function_call" in choice.delta:
                function_content_placeholder = stream_function_call(
                    function_call,
                    choice.delta.get("function_call", {}),
                    function_content_placeholder,
                )
            elif "delta" in choice and "content" in choice.delta:
                (
                    assistant_content,
                    assistant_content_placeholder,
                ) = stream_assistant_content(
                    assistant_content,
                    choice.delta.get("content", ""),
                    assistant_content_placeholder,
                )

            if choice["finish_reason"] == "function_call":
                function_content_placeholder = handle_complete_function_call(
                    function_call,
                    function_content_placeholder,
                )  # Resets function_placeholder to None
                break
            elif choice["finish_reason"] == "stop":
                assistant_responded = handle_complete_assistant_content(
                    assistant_content,
                    assistant_content_placeholder,
                )  # Sets assistant_responded to True to exit while loop
                break


def stream_function_call(
    function_call: dict,
    function_call_delta: dict,
    content_placeholder: DeltaGenerator | None,
) -> None:
    """Builds function call from stream. Returns placeholder."""
    function_call["name"] += function_call_delta.get("name", "")
    function_call["arguments"] += function_call_delta.get("arguments", "")
    if len(function_call["arguments"]) > 0:
        content_placeholder = show_message(
            "function",
            None,
            content_placeholder,
            function_call["name"],
            "running",
        )
    return content_placeholder


def stream_assistant_content(
    content: str,
    content_delta: str,
    content_placeholder: DeltaGenerator | None,
) -> tuple[DeltaGenerator, str]:
    """Streams content to placeholder. Returns content and placeholder."""
    content += content_delta
    content_placeholder = show_message(
        "assistant", content, content_placeholder
    )
    return content, content_placeholder


def handle_complete_function_call(
    function_call: dict,
    content_placeholder: DeltaGenerator,
) -> None:
    """Handles a function call."""
    chat_data.add_message("assistant", None, function_call)
    function_content = call_function(**function_call)
    chat_data.add_message(
        "function", function_content, name=function_call["name"]
    )
    show_message(
        "function",
        function_content,
        content_placeholder,
        function_call["name"],
        "complete",
    )
    return None


def handle_complete_assistant_content(
    content: str,
    content_placeholder: DeltaGenerator,
) -> bool:
    """Handles completed assistant content."""
    chat_data.add_message("assistant", content)
    show_message("assistant", content, content_placeholder)
    return True
