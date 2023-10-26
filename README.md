# Streamlit Chat Plus

> **Note**: This is more of a proof-of-concept than a production-ready app. At this point, for example, I haven't added any testing. Use at your own risk! Also note that I haven't done QA on the instructions for installation below. If you run into any issues, please let me know.

This is an LLM-powered chat app that uses a [Streamlit](https://streamlit.io) UI. It builds upon the standard Streamlit chat experience with the following:

* Streaming responses
* Function calling
* Chat history
* Memory (using embeddings)
* Chat sharing (warning: any user with access to your app can enter a URL at <url>.com?shared_chat_id=<chat_id> to see a chat; chats are public by default)

# Installation

* Get an [OpenAI API key](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key)
* Create a [Supabase](https://supabase.com/) account, project, and database
* Run `setup.sql` on your Supabase database
* Clone or download this repo
* Change `.streamlit/secrets_example.toml` to `.streamlit/secrets.toml` and add values for your OpenAI API key and Supabase URL and key

# Usage

Once you complete the above, you can navigate to the directory of this README file and run this in terminal:

```bash
streamlit run streamlit_app.py
```

