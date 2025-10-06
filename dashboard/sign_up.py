"""Script to allow users to sign up for email summaries or power outage alerts."""
import streamlit as st
from dotenv import load_dotenv
from psycopg2 import connect
from os import environ as ENV
from requests import get


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


def alert_subscription(name: str, email: str, postcode: str, addition: bool):
    """Subscribe a customer for outage alerts for a postcode."""

    customer_id = get_or_create_customer(name, email)
    if customer_id == -1:
        print("name and email do not match records")
        return

    if not verify_postcode(postcode):
        print("Invalid postcode")
        return
    print(postcode.upper())
    postcode_id = get_or_create_postcode(postcode.upper())

    if addition:
        create_postcode_subscription(customer_id, postcode_id)
    else:
        remove_postcode_subscription(customer_id, postcode_id)


def get_or_create_customer(name: str, email: str):
    """
    gets the postcode id or creates a postcode and returns id.
    Returns either customer id or -1 if name doesn't match email.
    """

    customer_query = """
        INSERT INTO customer (customer_name, customer_email, summary_subscription)
        VALUES (%s, %s, False)
        ON CONFLICT (customer_email) DO UPDATE
        SET customer_email = EXCLUDED.customer_email
        RETURNING customer_id;
        """

    verification_query = """
        SELECT customer_name 
        FROM customer
        WHERE customer_id = %s
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(customer_query, (name, email))

            customer_id = cur.fetchone()[0]

            cur.execute(verification_query, (customer_id,))

            customer_name = cur.fetchone()[0]

        if name != customer_name:
            return -1
        return customer_id


def verify_postcode(postcode: str):
    """Verify that a postcode is real."""
    base_url = "https://api.postcodes.io/postcodes/"
    postcode = postcode.replace(" ", "")

    response = get(f"{base_url}{postcode}")

    if response.status_code == 200:
        return True

    else:
        return False


def get_or_create_postcode(postcode: str):
    """gets the postcode id or creates a postcode and returns id."""
    query = """
    INSERT INTO postcode (postcode)
    VALUES (%s)
    ON CONFLICT (postcode) DO UPDATE
    SET postcode = EXCLUDED.postcode
    RETURNING postcode_id;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (postcode,))

            return cur.fetchone()[0]


def create_postcode_subscription(customer_id: int, postcode_id: int) -> None:
    """Inserts subscription into the customer/postcode link table"""

    existing_alert_query = """
        SELECT customer_postcode_link_id
        FROM customer_postcode_link
        WHERE customer_id = %s
        AND postcode_id = %s;
    """

    query = """
        INSERT INTO customer_postcode_link (customer_id, postcode_id)
        VALUES (%s, %s);
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(existing_alert_query, (customer_id, postcode_id))

            alert_id = cur.fetchone()

            if not alert_id:
                cur.execute(query, (customer_id, postcode_id))


def remove_postcode_subscription(customer_id: int, postcode_id: int) -> None:
    """Removes a subscription from the customer/postcode link table."""

    query = """
        DELETE FROM customer_postcode_link
        WHERE customer_id = %s
        AND postcode_id = %s
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (customer_id, postcode_id))


def remove_all_user_records(name: str, email: str):
    """Removes all user records from the database."""

    customer_id_query = """
        SELECT customer_id 
        FROM customer
        WHERE customer_email = %s
        AND customer_name = %s;
    """

    alerts_removal_query = """
        DELETE FROM customer_postcode_link
        WHERE customer_id = %s
    """

    customer_removal_query = """
        DELETE FROM customer
        WHERE customer_id = %s
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(customer_id_query, (email, name))

            customer_id = cur.fetchone()

            if not customer_id:
                print("No matching details recorded")
                return

            cur.execute(alerts_removal_query, (customer_id[0],))

            cur.execute(customer_removal_query, (customer_id[0],))

        print("Details removed.")


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
            alert_subscription(name_alert, email_alert, postcode_alert, True)
    with r:
        if st.button("unsubscribe", key=4):
            alert_subscription(name_alert, email_alert, postcode_alert, False)


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

st.header("Remove all records")
name_removal = st.text_input("name", key=9)
email_removal = st.text_input("email", key=10)
if st.button("Remove records", key=11):
    remove_all_user_records(name_removal, email_removal)
