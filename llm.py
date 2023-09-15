from functools import partial

import openai
import streamlit as st

openai.api_key = st.secrets["OPENAI_API_KEY"]

respond = partial(openai.ChatCompletion.create)


def embed(text: str) -> str:
    """Embeds text using OpenAI's API."""
    embedding = openai.Embedding.create(
        input=[text], model="text-embedding-ada-002"
    )
    return embedding["data"][0]["embedding"]
