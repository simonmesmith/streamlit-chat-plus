# Streamlit Chat Plus

This is a simple implementation (for now, anyway) of Streamlit chat functionality using the OpenAI API, with the addition of:

* Streaming text
* Function calls

To use it:

* Clone or otherwise copy this repository
* Install requirements with `pip install -r requirements.txt`
* Copy `example.env`, add your OpenAI API key, and save the file as .env
* Run the chat with `streamlit run app.py`

Currently, this has only one simple demonstration function called `multiply`. You can create more functions by following that example in `llm_functions.py`.
