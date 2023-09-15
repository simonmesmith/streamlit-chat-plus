import streamlit as st
from streamlit.delta_generator import DeltaGenerator

import chat_data
from llm import respond
from llm_functions import call_function, functions


def show_function_message(
    content: str | None = None,
    placeholder: DeltaGenerator | None = None,
    name: str | None = "function",
) -> DeltaGenerator:
    """Shows a function message."""
    if not placeholder:
        with st.chat_message("function"):
            with st.expander(f"Calling function: {name}"):
                placeholder = st.empty()
    placeholder.markdown(content)
    return placeholder


def show_assistant_message(
    content: str | None, placeholder: DeltaGenerator | None
) -> DeltaGenerator:
    """Shows an assistant message."""
    if not placeholder:
        with st.chat_message("assistant"):
            placeholder = st.empty()
    placeholder.markdown(content)
    return placeholder


def show_user_message(
    content: str | None, placeholder: DeltaGenerator | None
) -> DeltaGenerator:
    """Shows a user message."""
    if not placeholder:
        with st.chat_message("user"):
            placeholder = st.empty()
    placeholder.markdown(content)
    return placeholder


def show_message(
    role: str,
    content: str,
    placeholder: DeltaGenerator | None = None,
    name: str | None = None,
) -> None:
    """Shows a message."""
    if role == "function":
        placeholder = show_function_message(content, placeholder, name)
    elif role == "assistant":
        placeholder = show_assistant_message(content, placeholder)
    elif role == "user":
        placeholder = show_user_message(content, placeholder)
    else:
        raise ValueError(f"Invalid role: {role}")
    return placeholder


def show_existing_messages() -> None:
    """Shows existing messages."""
    for msg in st.session_state.chat.messages:
        if msg["role"] in ["user", "assistant"] and msg["content"]:
            show_message(msg["role"], msg["content"])
        elif msg["role"] == "function":
            show_message(msg["role"], msg["content"], name=msg["name"])


def stream_function_call(
    function_call: dict,
    function_call_delta: dict,
    placeholder: DeltaGenerator | None,
) -> None:
    """Builds function call from stream. Returns placeholder."""
    function_call["name"] += function_call_delta.get("name", "")
    function_call["arguments"] += function_call_delta.get("arguments", "")
    if len(function_call["arguments"]) > 0:
        placeholder = show_message(
            "function", None, placeholder, function_call["name"]
        )
    return placeholder


def stream_assistant_content(
    content: str,
    content_delta: str,
    placeholder: DeltaGenerator | None,
) -> tuple[DeltaGenerator, str]:
    """Streams content to placeholder. Returns content and placeholder."""
    content += content_delta
    placeholder = show_message("assistant", content, placeholder)
    return content, placeholder


def handle_complete_function_call(
    function_call: dict,
    placeholder: DeltaGenerator,
) -> None:
    """Handles a function call."""
    chat_data.add_message("assistant", None, function_call)
    function_content = call_function(**function_call)
    chat_data.add_message(
        "function", function_content, name=function_call["name"]
    )
    show_message(
        "function", function_content, placeholder, function_call["name"]
    )
    return None


def handle_complete_assistant_content(
    content: str,
    placeholder: DeltaGenerator,
) -> bool:
    """Handles completed assistant content."""
    chat_data.add_message("assistant", content)
    show_message("assistant", content, placeholder)
    return True


def run_response_loop():
    """Runs the response loop."""
    assistant_responded = False
    while not assistant_responded:
        assistant_content = ""
        assistant_placeholder = None
        function_call = {"name": "", "arguments": ""}
        function_placeholder = None

        response = respond(
            model="gpt-4",
            functions=functions,
            messages=st.session_state.chat.messages,
            stream=True,
        )

        for chunk in response:
            choice = chunk["choices"][0]
            if "delta" in choice and "function_call" in choice.delta:
                function_placeholder = stream_function_call(
                    function_call,
                    choice.delta.get("function_call", {}),
                    function_placeholder,
                )
            elif "delta" in choice and "content" in choice.delta:
                (
                    assistant_content,
                    assistant_placeholder,
                ) = stream_assistant_content(
                    assistant_content,
                    choice.delta.get("content", ""),
                    assistant_placeholder,
                )

            if choice["finish_reason"] == "function_call":
                function_placeholder = handle_complete_function_call(
                    function_call,
                    function_placeholder,
                )  # Resets function_placeholder to None
                break
            elif choice["finish_reason"] == "stop":
                assistant_responded = handle_complete_assistant_content(
                    assistant_content,
                    assistant_placeholder,
                )  # Sets assistant_responded to True to exit while loop
                break
