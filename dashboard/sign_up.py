"""Script to allow users to sign up for email summaries or power outage alerts."""
import streamlit as st
from dotenv import load_dotenv
from psycopg2 import connect
from os import environ as ENV


@st.cache_resource
def get_db_connection():
    """Connect to the postgres database managed by RDS."""
    load_dotenv()

    return connect(database=ENV["DB_NAME"],
                   user=ENV["DB_USERNAME"],
                   password=ENV["DB_PASSWORD"],
                   host=ENV["DB_HOST"],
                   port=ENV["DB_PORT"])


def summary_subscription(name: str, email: str, status: bool):
    """Upsert customers table to adjust summary subscription status."""
    query = """
    INSERT INTO customer (customer_name, customer_email, summary_subscription)
    VALUES (%s, %s, %s)
    ON CONFLICT (customer_email) DO UPDATE
    SET summary_subscription = EXCLUDED.summary_subscription;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (name, email, status))


st.header("Sign up page")


left, right = st.columns(2, vertical_alignment="top")

with left:
    st.header("Outage alerts")
    name_alert = st.text_input("name", key=1)
    email_alert = st.text_input("email", key=2)
    postcode_alert = st.text_input("postcode")

    l, r = st.columns(2)
    with l:
        if st.button("subscribe", key=3):
            pass

    with r:
        if st.button("unsubscribe", key=4):
            pass


with right:
    st.header("Summary reports")
    name_summary = st.text_input("name", key=5)
    email_summary = st.text_input("email", key=6)

    first, second = st.columns(2)
    with first:
        if st.button("subscribe", key=7):
            summary_subscription(name_summary, email_summary, True)
            print("subscribed to summary")

    with second:
        if st.button("unsubscribe", key=8):
            summary_subscription(name_summary, email_summary, False)
            print('Unsubscribed to summary')
