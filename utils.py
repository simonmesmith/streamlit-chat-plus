"""Utility functions for the app."""

import urllib

import streamlit as st


def get_base_url() -> str:
    """Returns the base URL of the current Streamlit app."""
    session = st.runtime.get_instance()._session_mgr.list_active_sessions()[0]
    return urllib.parse.urlunparse(
        [
            session.client.request.protocol,
            session.client.request.host,
            "",
            "",
            "",
            "",
        ]
    )


def get_shared_chat_id() -> int | None:
    """Returns the shared chat ID from the URL."""
    if "shared_chat_id" not in st.experimental_get_query_params():
        return None
    return int(st.experimental_get_query_params()["shared_chat_id"][0])
