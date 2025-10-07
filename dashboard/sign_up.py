"""Script to allow users to sign up for email summaries or power outage alerts."""
import streamlit as st
from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extensions import connection
from os import environ as ENV
from requests import get


@st.cache_resource
def get_db_connection() -> connection:
    """Connect to the postgres database managed by RDS."""
    load_dotenv()

    return connect(database=ENV["DB_NAME"],
                   user=ENV["DB_USERNAME"],
                   password=ENV["DB_PASSWORD"],
                   host=ENV["DB_HOST"],
                   port=ENV["DB_PORT"])


def summary_subscription(conn: connection, name: str, email: str, status: bool) -> None:
    """Upsert customers table to adjust summary subscription status."""
    query = """
    UPDATE customer 
    SET summary_subscription = %s
    WHERE customer_id = %s
    AND summary_subscription IS DISTINCT FROM %s
    RETURNING summary_subscription;
    """

    customer_id = get_or_create_customer(conn, name, email)
    if customer_id == -1:
        st.warning("name and email do not match records")
        return

    with conn.cursor() as cur:
        cur.execute(query, (status, customer_id, status))

        res = cur.fetchone()

        conn.commit()

    if res is None:
        if status == True:
            st.info("Subscription already exists")
        else:
            st.info("Subscription did not exist")
    elif res[0] == True:
        st.success("Subscription made")
    elif res[0] == False:
        st.success("subscription removed")


def alert_subscription(conn: connection, name: str, email: str, postcode: str, is_addition: bool) -> None:
    """Subscribe a customer for outage alerts for a postcode."""

    customer_id = get_or_create_customer(conn, name, email)
    if customer_id == -1:
        st.warning("name and email do not match records")
        return

    is_valid_postcode, formatted_postcode = verify_postcode(postcode)
    if not is_valid_postcode:
        st.warning("Invalid postcode")
        return
    postcode_id = get_or_create_postcode(conn, formatted_postcode)

    if is_addition:
        create_postcode_subscription(conn, customer_id, postcode_id)
    else:
        remove_postcode_subscription(conn, customer_id, postcode_id)


def get_or_create_customer(conn: connection, name: str, email: str) -> int:
    """
    Gets the postcode id or creates a postcode and returns id.
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

    with conn.cursor() as cur:
        cur.execute(customer_query, (name.title(), email))

        customer_id = cur.fetchone()[0]

        cur.execute(verification_query, (customer_id,))

        customer_name = cur.fetchone()[0]

        conn.commit()

    if name.title() != customer_name:
        return -1
    return customer_id


def verify_postcode(postcode: str) -> tuple:
    """Verify that a postcode is real."""
    base_url = "https://api.postcodes.io/postcodes/"
    postcode = postcode.replace(" ", "")

    response = get(f"{base_url}{postcode}")

    if response.status_code == 200:
        return True, response.json()['result']['postcode']
    return False, None


def get_or_create_postcode(conn: connection, postcode: str) -> int:
    """gets the postcode id or creates a postcode and returns id."""
    query = """
    INSERT INTO postcode (postcode)
    VALUES (%s)
    ON CONFLICT (postcode) DO UPDATE
    SET postcode = EXCLUDED.postcode
    RETURNING postcode_id;
    """

    with conn.cursor() as cur:
        cur.execute(query, (postcode,))

        conn.commit()

        return cur.fetchone()[0]


def create_postcode_subscription(conn: connection, customer_id: int, postcode_id: int) -> None:
    """Inserts subscription into the customer/postcode link table"""

    existing_alert_query = """
        SELECT customer_postcode_link_id
        FROM customer_postcode_link
        WHERE customer_id = %s
        AND postcode_id = %s;
    """

    create_alert_query = """
        INSERT INTO customer_postcode_link (customer_id, postcode_id)
        VALUES (%s, %s);
    """

    with conn.cursor() as cur:
        cur.execute(existing_alert_query, (customer_id, postcode_id))

        alert_id = cur.fetchone()

        if not alert_id:
            cur.execute(create_alert_query, (customer_id, postcode_id))
            st.success("Alert created")
        else:
            st.info("Alert already exists")

        conn.commit()


def remove_postcode_subscription(conn: connection, customer_id: int, postcode_id: int) -> None:
    """Removes a subscription from the customer/postcode link table."""

    query = """
        DELETE FROM customer_postcode_link
        WHERE customer_id = %s
        AND postcode_id = %s
        RETURNING customer_postcode_link_id;
    """

    with conn.cursor() as cur:
        cur.execute(query, (customer_id, postcode_id))

        res = cur.fetchone()

        if res:
            st.success("Alert Removed")
        else:
            st.info("Alert did not exist")

        conn.commit()


def remove_all_user_records(conn: connection, name: str, email: str) -> None:
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

    with conn.cursor() as cur:
        cur.execute(customer_id_query, (email, name.title()))

        customer_id = cur.fetchone()

        if not customer_id:
            st.info("No matching details recorded")
            return

        cur.execute(alerts_removal_query, (customer_id[0],))

        cur.execute(customer_removal_query, (customer_id[0],))

        conn.commit()

    st.success("Details removed.")


if __name__ == "__main__":

    conn = get_db_connection()

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
                alert_subscription(conn, name_alert, email_alert,
                                   postcode_alert, True)
        with r:
            if st.button("unsubscribe", key=4):
                alert_subscription(conn, name_alert, email_alert,
                                   postcode_alert, False)

    with right:
        st.header("Summary reports")
        name_summary = st.text_input("name", key=5)
        email_summary = st.text_input("email", key=6)

        first, second = st.columns(2)
        with first:
            if st.button("subscribe", key=7):
                summary_subscription(conn, name_summary, email_summary, True)

        with second:
            if st.button("unsubscribe", key=8):
                summary_subscription(conn, name_summary, email_summary, False)

    st.header("Remove all records")
    name_removal = st.text_input("name", key=9)
    email_removal = st.text_input("email", key=10)
    if st.button("Remove records", key=11):
        remove_all_user_records(conn, name_removal, email_removal)
