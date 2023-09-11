import os
from functools import partial

import openai
from dotenv import load_dotenv

from llm_functions import functions

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_MESSAGE = "You are an AI chatbot with functions."

respond = partial(
    openai.ChatCompletion.create,
    model="gpt-4",
    functions=functions,
    stream=True,
)
