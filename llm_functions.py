import json

import streamlit as st

from db import db_client
from llm import embed

_functions_dict = {
    "remember": {
        "name": "remember",
        "description": "Remember information for future reference.",
        "parameters": {
            "type": "object",
            "properties": {
                "memory": {
                    "type": "string",
                    "description": "The information you want to remember.",
                },
            },
            "required": ["memory"],
        },
    },
    "recall": {
        "name": "recall",
        "description": "Recall information from memory.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "A natural language query to retrieve a memory."
                    ),
                },
            },
            "required": ["query"],
        },
    },
}
functions = list(_functions_dict.values())  # Export for OpenAI as an array


def call_function(name: str, arguments: str) -> str:
    """Calls a function and returns the result."""

    # Ensure the function is defined
    if name not in _functions_dict:
        return "Function not defined."

    # Convert the function arguments from a string to a dict
    function_arguments_dict = json.loads(arguments)

    # Ensure the function arguments are valid
    function_parameters = _functions_dict[name]["parameters"]["properties"]
    for argument in function_arguments_dict:
        if argument not in function_parameters:
            return f"{argument} not defined."

    # Call the function and return the result
    return globals()[name](**function_arguments_dict)


def remember(memory: str) -> str:
    """Remembers information for future reference."""
    embedding = embed(memory)
    db_client().table("memories").insert(
        {
            "user_email": st.experimental_user.email,
            "memory_text": memory,
            "memory_embedding": embedding,
        }
    ).execute()
    return "Remembered."


def recall(query: str) -> str:
    """Recalls information from memory."""
    query_embedding = embed(query)
    memories = (
        db_client()
        .rpc(
            "recall_memories",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.8,
                "match_count": 10,
            },
        )
        .eq("user_email", st.experimental_user.email)
        .execute()
    )
    if len(memories.data) == 0:
        return "No memories found."
    return "Remembered:\n\n" + "\n\n".join(
        [m["memory_text"] for m in memories.data]
    )
