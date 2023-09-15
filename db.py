import streamlit as st
from supabase import Client, create_client


@st.cache_resource
def db_client() -> Client:
    """Initialize connection to Supabase DB."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]  # Secret, non-public key
    return create_client(url, key)
