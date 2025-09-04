import streamlit as st
from functions import classify_query, generate_sql, get_general_knowledge, format_student_results
from database import execute_sql, test_connection
import time
from functools import lru_cache

@lru_cache(maxsize=50)
def cached_execute_sql(sql: str) -> list:
    return execute_sql(sql)

def main():
    st.set_page_config(page_title="Query Assistant", layout="wide")

    if 'last_query' not in st.session_state:
        st.session_state.last_query = None
        st.session_state.last_result = None


    st.title("chatbot")

    if hasattr(st.session_state, 'db_tables'):
        st.write("Connected to database. Tables:", st.session_state.db_tables)

    query = st.text_input("Enter your query:")

    if st.button("Submit"):
        if not query:
            st.warning("Please enter a query.")
        else:
            start_time = time.time()

            with st.spinner("Processing..."):
                if query == st.session_state.last_query and st.session_state.last_result:
                    st.success(st.session_state.last_result)
                else:
                    classification = classify_query(query)

                    if classification == "student":
                        try:
                            sql = generate_sql(query)
                            result = cached_execute_sql(sql)
                            answer = format_student_results(query, result)

                            st.session_state.last_query = query
                            st.session_state.last_result = answer

                            st.success(answer)
                        except Exception as e:
                            st.error(f"Database error: {e}")
                    else:
                        answer = get_general_knowledge(query)
                        st.markdown(answer)

            st.write(f"Processed in {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
