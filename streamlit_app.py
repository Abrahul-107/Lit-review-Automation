import streamlit as st
import pandas as pd
from ResearchPaperAccess.arxiv_dataset_access import search_by_title
from LLM_Calls.llama_ratings import get_rating

st.set_page_config(page_title="Literature review System", layout="wide")

st.title("Literature review System")

st.sidebar.title("Search by")
option = st.sidebar.radio("Choose an option", ("Keyword", "PDF"))

user_keywords = ""

if option == "Keyword":
    user_keywords = st.text_input("Enter the keywords separated by comma:")
    if user_keywords:
        st.write(f"You entered the keyword: {user_keywords}")
    else:
        st.write("Please enter a keyword.")

elif option == "PDF":
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        st.write(f"You uploaded: {uploaded_file.name}")
    else:
        st.write("Please upload a PDF file.")

search_button = st.button("Search")

# --- Session State Initialization ---
if "page" not in st.session_state:
    st.session_state.page = 0
if "all_data" not in st.session_state:
    st.session_state.all_data = pd.DataFrame()
if "accepted_titles" not in st.session_state:
    st.session_state.accepted_titles = []  # List to store accepted titles
if "accepted_status" not in st.session_state:
    st.session_state.accepted_status = {}  # Dictionary to store accept/decline status
if "declined_status" not in st.session_state:
    st.session_state.declined_status = {}


# --- Pagination Functions ---
def next_page(total_pages):
    if st.session_state.page < total_pages - 1:
        st.session_state.page += 1


def prev_page():
    if st.session_state.page > 0:
        st.session_state.page -= 1


# --- Search and Data Preparation ---
if search_button and user_keywords:
    ar_responses = search_by_title(user_keywords)

    # call Llama to get the ratings
    ratings = get_rating(ar_responses)
    data = []
    for i, response in enumerate(ar_responses):
        data.append(
            {
                "Title": response.title,
                "URL": response.pdf_url,
                "Published": response.published,
                "Rating": ratings.get(response.title, "N/A"),
                "Accept": f"accept_{i}",
                "Decline": f"decline_{i}",
            }
        )
    st.session_state.all_data = pd.DataFrame(data)
    st.session_state.page = 0

    # Initialize accept/decline status for the new search results
    for i in range(len(st.session_state.all_data)):
        st.session_state.accepted_status[f"accept_{i}"] = False
        st.session_state.declined_status[f"decline_{i}"] = False


# --- Pagination and Display ---
items_per_page = 5
if not st.session_state.all_data.empty:
    total_pages = (
        len(st.session_state.all_data) + items_per_page - 1
    ) // items_per_page
    start_index = st.session_state.page * items_per_page
    end_index = min(
        (st.session_state.page + 1) * items_per_page, len(st.session_state.all_data)
    )
    current_page_df = st.session_state.all_data[start_index:end_index]

    # column header
    cols = st.columns([3,2,1,1,1,1], border=True)
    with cols[0]:
        st.write("**Title**")
    with cols[1]:
        st.write("**URL**")
    with cols[2]:
        st.write("**Published**")
    with cols[3]:
        st.write("**Rating**")
    with cols[4]:
        st.write("**Accept**")
    with cols[5]:
        st.write("**Decline**")

    def create_button_cells(df):
        for index, row in df.iterrows():
            cols = st.columns([3,2,1,1,1,1], border=True)
            with cols[0]:
                st.write(row["Title"])
            with cols[1]:
                st.write(row["URL"])
            with cols[2]:
                st.write(row["Published"])
            with cols[3]:
                st.write(row["Rating"])
            with cols[4]:
                # Accept Button Logic
                if st.button(
                    "✓",
                    key=row["Accept"],
                    disabled=st.session_state.accepted_status[row["Accept"]],
                ):
                    st.session_state.accepted_status[row["Accept"]] = (
                        True  # Disable after click
                    )
                    st.session_state.declined_status[row["Decline"]] = (
                        False  # if accept is clicked then decline should be false
                    )
                    if row["Title"] not in st.session_state.accepted_titles:
                        st.session_state.accepted_titles.append(row["Title"])

            with cols[5]:
                # Decline Button Logic
                if st.button(
                    "❌",
                    key=row["Decline"],
                    disabled=st.session_state.declined_status[row["Decline"]],
                ):
                    st.session_state.declined_status[row["Decline"]] = (
                        True  # Disable after click
                    )
                    st.session_state.accepted_status[row["Accept"]] = (
                        False  # if decline is clicked then accept should be false
                    )
                    if row["Title"] in st.session_state.accepted_titles:
                        st.session_state.accepted_titles.remove(row["Title"])

    create_button_cells(current_page_df)

    # --- Navigation Buttons ---
    col1, col2 = st.columns([2, 2])
    with col1:
        if st.session_state.page > 0:
            st.button("Previous", on_click=prev_page)
    with col2:
        if st.session_state.page < total_pages - 1:
            st.button("Next", on_click=next_page, args=(total_pages,))
    # --- End Navigation Buttons ---

    st.write("Accepted Titles:")
    st.write(st.session_state.accepted_titles)

elif search_button:
    st.write("Please enter keywords to search.")
