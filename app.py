import streamlit as st
import pandas as pd
from query_generator import generate_query
from query_executor import execute_sql_query, execute_mongodb_query, detect_database
from schemas import schemas
import json

st.set_page_config(page_title="Natural Language to Query")

if "query_complete" not in st.session_state:
    st.session_state.query_complete = False
if "query_input_value" not in st.session_state:
    st.session_state.query_input_value = ""

st.title("🧠 Natural Language to SQL and MongoDB Query")
st.write("Enter your question and select the database type if needed:")

if st.button("Clear Cache"):
    st.cache_data.clear()
    st.session_state.query_complete = False
    st.rerun()

# Query input
user_query = st.text_input(
    "Your Query",
    value=st.session_state.query_input_value,
    placeholder="e.g., List products from Bike Store",
    key="user_query_input",
    disabled=st.session_state.query_complete,
)

if user_query != st.session_state.query_input_value:
    st.session_state.query_input_value = user_query

# Database selection
databases = ["Bike Store", "AdventureWorks", "FIFA"]
selected_db = None

if user_query:
    detected_db = detect_database(user_query)
    if not detected_db:
        st.warning(
            "Please select a database: 'Bike Store', 'AdventureWorks', or 'FIFA'."
        )
        selected_db = st.selectbox(
            "Select a database:", [""] + databases, key="db_select"
        )
        final_db = selected_db if selected_db else None
    else:
        final_db = detected_db

    if final_db and not st.session_state.query_complete:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate SQL Query", key="sql_button"):
                with st.spinner("Generating SQL query..."):
                    try:
                        query = generate_query(
                            user_query, query_type="sql", schemas=schemas, database = final_db
                        )
                        if query:
                            st.code(query, language="sql")
                            with st.spinner("Executing SQL query..."):
                                try:
                                    results = execute_sql_query(query, final_db)
                                    if isinstance(results, tuple) and len(results) == 2:
                                        data, columns = results
                                        if data and columns:
                                            df = pd.DataFrame(data, columns=columns)
                                            st.write("Results:")
                                            st.dataframe(
                                                df, use_container_width=True, height=400
                                            )
                                        else:
                                            df = pd.DataFrame(columns=columns)
                                            st.write("Results (No data):")
                                            st.dataframe(df, use_container_width=True)
                                            st.info("No results returned.")
                                    elif isinstance(results, int):
                                        st.info(f"Query affected {results} rows.")
                                    else:
                                        st.error(f"Unexpected result format: {results}")
                                except Exception as db_error:
                                    st.error(
                                        f"Database execution error: {str(db_error)}"
                                    )
                                finally:
                                    st.cache_data.clear()
                        else:
                            st.error("No SQL query generated.")
                    except Exception as gen_error:
                        st.error(f"Query generation error: {str(gen_error)}")
                st.session_state.query_complete = True

        with col2:
            if st.button("Generate MongoDB Query", key="mongodb_button"):
                with st.spinner("Generating MongoDB query..."):
                    try:
                        query = generate_query(
                            user_query, query_type="mongodb", schemas=schemas, database = final_db
                        )
                        if query:
                            st.code(query, language="javascript")
                            with st.spinner("Executing MongoDB query..."):
                                try:
                                    results = execute_mongodb_query(query, final_db)
                                    if isinstance(results, list) and results:
                                        st.write("Results:")
                                        # Add custom CSS for scrollable container
                                        st.markdown(
                                            """
                                            <style>
                                            .scrollable-json {
                                                max-height: 400px;
                                                overflow-y: auto;
                                            }
                                            </style>
                                            """,
                                            unsafe_allow_html=True,
                                        )
                                        # Format JSON and display in scrollable container
                                        formatted_json = json.dumps(
                                            results, indent=4, default=str
                                        )
                                        st.markdown(
                                            f'<div class="scrollable-json"><pre><code>{formatted_json}</code></pre></div>',
                                            unsafe_allow_html=True,
                                        )
                                    elif isinstance(results, dict):
                                        st.write("Operation Result:")
                                        st.markdown(
                                            """
                                            <style>
                                            .scrollable-json {
                                                max-height: 400px;
                                                overflow-y: auto;
                                            }
                                            </style>
                                            """,
                                            unsafe_allow_html=True,
                                        )
                                        # Format JSON and display in scrollable container
                                        formatted_json = json.dumps(results, indent=4)
                                        st.markdown(
                                            f'<div class="scrollable-json"><pre><code>{formatted_json}</code></pre></div>',
                                            unsafe_allow_html=True,
                                        )
                                    elif not results:
                                        st.info("No results returned.")
                                    else:
                                        st.error(f"Unexpected result format: {results}")
                                except Exception as db_error:
                                    st.error(
                                        f"Database execution error: {str(db_error)}"
                                    )
                    except Exception as gen_error:
                        st.error(f"Query generation error: {str(gen_error)}")
                st.session_state.query_complete = True

if st.session_state.query_complete:
    if st.button("Enter New Query", key="new_query_button"):
        # Reset query_complete state
        st.session_state.query_complete = False
        # Reset the query input value
        st.session_state.query_input_value = ""
        st.rerun()
    st.write("Click 'Enter New Query' to proceed with a new question.")
else:
    st.warning("Please enter a query.")
