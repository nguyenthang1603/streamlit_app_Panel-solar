import streamlit as st
from streamlit_option_menu import option_menu
from vega_datasets import data
import altair as alt
import pandas as pd


st.set_page_config(
    page_title="Solar Battery Data Analysis", page_icon="⬇", layout="centered"
)
# Create an empty container
placeholder = st.empty()

actual_email = "Panel"
actual_password = "123456"

# Initialize a session state variable for login status
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False

# If the user is not logged in, display the login form
if not st.session_state.is_authenticated:
    # Insert a form in the container
    with placeholder.form("login"):
        st.markdown("#### Enter your credentials")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit and email == actual_email and password == actual_password:
        # If the form is submitted and the email and password are correct,
        # clear the form/container and set authentication to True
        placeholder.empty()
        st.session_state.is_authenticated = True
        st.success("Login successful")

# If authenticated, display the option menu
if st.session_state.is_authenticated:
    with st.sidebar:
        selected = option_menu(
            menu_title=None,
            options=["Home", "Chart", "Log out"],
        )
    if selected == "Home":
        st.write("This is home page")
    elif selected == "Chart":
        @st.cache_data
        def get_data():
            source = data.stocks()
            source = source[source.date.gt("2004-01-01")]
            return source

        @st.cache_data(ttl=60 * 60 * 24)
        def get_chart(data):
            hover = alt.selection_single(
                fields=["date"],
                nearest=True,
                on="mouseover",
                empty="none",
            )

            lines = (
                alt.Chart(data, height=500, title="Demo")
                .mark_line()
                .encode(
                    x=alt.X("date", title="Date"),
                    y=alt.Y("price", title="Price"),
                    color="symbol",
                )
            )

            # Draw points on the line, and highlight based on selection
            points = lines.transform_filter(hover).mark_circle(size=65)

            # Draw a rule at the location of the selection
            tooltips = (
                alt.Chart(data)
                .mark_rule()
                .encode(
                    x="yearmonthdate(date)",
                    y="price",
                    opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
                    tooltip=[
                        alt.Tooltip("date", title="Date"),
                        alt.Tooltip("price", title="Price (USD)"),
                    ],
                )
                .add_selection(hover)
            )

            return (lines + points + tooltips).interactive()


        st.title("Solar Battery Data Analysis")

        col1, col2, col3 = st.columns(3)
        with col1:
            ticker = st.text_input("Choose a ticker (⬇💬👇ℹ️ ...)", value="⬇")
        with col2:
            ticker_dx = st.slider(
                "Horizontal offset", min_value=-30, max_value=30, step=1, value=0
            )
        with col3:
            ticker_dy = st.slider(
                "Vertical offset", min_value=-30, max_value=30, step=1, value=-10
            )

        # Original time series chart. Omitted `get_chart` for clarity
        source = get_data()
        chart = get_chart(source)

        # Input annotations
        ANNOTATIONS = [
            ("Mar 01, 2008", "Pretty good day for GOOG"),
            ("Dec 01, 2007", "Something's going wrong for GOOG & AAPL"),
            ("Nov 01, 2008", "Market starts again thanks to..."),
            ("Dec 01, 2009", "Small crash for GOOG after..."),
        ]

        # Create a chart with annotations
        annotations_df = pd.DataFrame(ANNOTATIONS, columns=["date", "event"])
        annotations_df.date = pd.to_datetime(annotations_df.date)
        annotations_df["y"] = 0
        annotation_layer = (
            alt.Chart(annotations_df)
            .mark_text(size=15, text=ticker, dx=ticker_dx, dy=ticker_dy, align="center")
            .encode(
                x="date:T",
                y=alt.Y("y:Q"),
                tooltip=["event"],
            )
            .interactive()
        )

        # Display both charts together
        st.altair_chart((chart + annotation_layer).interactive(), use_container_width=True)
    elif selected == "Log out":
        # Log out: Set authentication to False and display the login form again
        st.session_state.is_authenticated = False
        placeholder.empty()
else:
    selected = None
