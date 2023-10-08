import streamlit as st
import pandas as pd
import os

# Define the folder path where .xlsx files are located
folder_path = "Quizzes Container"

# Get a list of .xlsx files in the folder
xlsx_files = [file for file in os.listdir(
    folder_path) if file.endswith(".xlsx")]

# Define the CSS for styling with text-align set to "right" and custom input styling
app_alignment_css = """
<style>
    .stContainer {
        border: none !important;
    }
    body {
        direction: rtl;
        display: flex;
        flex-direction: column;
        border-top: 2px solid #ccc; /* Adjust color and width as needed */
        border-bottom: 2px solid #ccc;
        height: 90vh; /* Set the height to 90% of the viewport height */
        margin: 0; /* Remove default body margin */
        overflow-y: hidden; /* Hide vertical scrollbar */
    }
    input[type="text"] {
        width: max-content;
        margin-right: 5px;
        margin-left: 5px;
        font-size: 16px; /* Adjust the font size as needed */
    }
    .main-container {
        width: 90% !important;
        margin: 0 auto !important;
        flex: 1; /* Allows container to expand and consume available space */
        display: flex;
        flex-direction: column;
    }
    .element-container {
        width: 100% !important;
    }
    .stTextArea, .stText {
        width: 100% !important;
    }
    .stButton>button {
        width: max-content;
        width: 100%;
    }
    .header, .subheader {
        margin-top: 0; /* Remove default top margin from headers */
    }
    .save-button {
        background-color: #4CAF50; /* Original color (green) */
        transition: background-color 1s ease-in-out; /* Transition effect for color change */
    }
    .save-button.saved {
        background-color: #8BC34A !important; /* Faded green when saved */
    }
</style>
"""

# Set the direction to right-to-left (RTL) for the entire app
st.markdown(app_alignment_css, unsafe_allow_html=True)

# Create a sidebar dropdown for selecting a file to edit
selected_file = st.sidebar.selectbox("حدد ملفًا للتعديل عليه:", xlsx_files)

# Construct the full path of the selected file
selected_file_path = os.path.join(folder_path, selected_file)

# Check if a file is selected
if selected_file:
    # Function to load and edit the selected file
    def edit_selected_file():
        # Read the Excel file data
        data = pd.read_excel(selected_file_path)

        # Check if the required columns exist in the DataFrame
        required_columns = ['Course Name', 'V', 'P', 'Question Type', 'Question', 'Choice 1',
                            'Choice 2', 'Choice 3', 'Choice 4', 'Choice 5', 'Choice 6', 'Right Answer']
        missing_columns = [
            col for col in required_columns if col not in data.columns]
        if missing_columns:
            st.error(
                f"الملف المحدد يحتوي على أعمدة مفقودة: {', '.join(missing_columns)}. يرجى التأكد من أن التنسيق صحيح.")
            return

        # Page for displaying and editing questions
        file_path = selected_file_path

        try:
            # Read the Excel file data
            data = pd.read_excel(file_path)

            # Function to save changes to the Excel file
            def save_changes_to_excel(data, file_path):
                try:
                    data.to_excel(file_path, index=False)
                    st.success(
                        f"تم حفظ التعديلات بنجاح في: {selected_file_path}")
                except Exception as e:
                    st.error(
                        f"حدث خطأ أثناء حفظ التغييرات: {str(e)}")

            # Page for displaying questions

            def page2(data):
                # Ensure the current_question_idx is initialized and within bounds
                current_question_idx = st.session_state.get(
                    "current_question_idx", 0)
                current_question_idx = max(
                    0, min(current_question_idx, len(data) - 1))

                # Fetch necessary data
                course_name = data.iloc[current_question_idx]['Course Name']
                v_value = data.iloc[current_question_idx]['V']
                p_value = data.iloc[current_question_idx]['P']
                question_type = data.iloc[current_question_idx]['Question Type']

                # Render header and subheader at the top
                st.markdown(
                    f"<h1 class='header'>{course_name}</h1>", unsafe_allow_html=True)
                st.markdown(
                    f"<h5 class='subheader'>الفيديو {v_value} في الفقرة {p_value}</div>", unsafe_allow_html=True)

                # Display "توجه للسؤال الذي تريده" and "نوع السؤال" fields in two columns in the same row
                col1, col2 = st.columns(2)
                with col1:
                    question_indices = list(range(1, len(data) + 1))
                    selected_question_idx = st.selectbox(
                        "توجه للسؤال الذي تريده:", question_indices, index=current_question_idx)

                with col2:
                    # Display the question type as an editable text input
                    question_type = st.text_input(
                        "نوع السؤال", question_type, key="Question_Type")

                # Update the current_question_idx based on the selected index (0-based index)
                current_question_idx = selected_question_idx - 1
                st.session_state["current_question_idx"] = current_question_idx

                # Display the question and choices with the selected question index
                question_container = st.container()
                with question_container:
                    question_text = data.iloc[current_question_idx]['Question']
                    # Calculate the required height
                    text_height = len(question_text.split('\n')) * 25
                    question = st.text_area(
                        f"السؤال رقم {selected_question_idx}",
                        question_text,
                        key=f"Question_{selected_question_idx}",
                        height=text_height
                    )

                    # Create two columns to display answer choices 1 & 2 in the same row and 3 & 4 in the same row
                    col1, col2, col3 = st.columns(3)

                    # Initialize an empty list to store the edited choices
                    edited_choices = []

                    # Define a function to display choices in a column
                    def display_choices(column, start_idx, end_idx):
                        nonlocal edited_choices  # Allow the function to modify the variable outside its scope
                        choices = [data.iloc[current_question_idx][f'Choice {i}']
                                   for i in range(start_idx, end_idx + 1)]
                        for i, choice in enumerate(choices, start=start_idx):
                            # Replace NaN with an empty string
                            choice_value = "" if pd.isna(choice) else choice
                            edited_choice = column.text_input(
                                f"الإجابة رقم {i}", choice_value, key=f"Choice_{i}")
                            edited_choices.append(edited_choice)

                    # Displaying answer choices 1 & 2 in the first column
                    display_choices(col1, 1, 2)

                    # Displaying answer choices 3 & 4 in the second column
                    display_choices(col2, 3, 4)

                    # Displaying answer choices 5 & 6 in the third column
                    display_choices(col3, 5, 6)

                # Display the correct answer (editable field)
                correct_answer = st.text_input(
                    "الاختيار الصحيح", data.iloc[current_question_idx]['Right Answer'], key=f"Correct_Answer_{current_question_idx}")

                # Button handlers
                button_container = st.container()
                with button_container:
                    # Adjust the column proportions as needed
                    col1, col2, col3, col4 = st.columns([1, 3, 1, 1])

                    if col1.button("السؤال السابق") and current_question_idx > 0:
                        with st.spinner("جاري التحميل..."):
                            current_question_idx -= 1
                            st.session_state["current_question_idx"] = current_question_idx

                    col2.empty()  # Empty column to create space
                    # Add a CSS class to the save button for color change on success
                    save_button = col4.button(
                        "احفظ التعديلات", key="Save_Button")
                    if save_button:
                        try:
                            # Update the DataFrame with edited question, answer choices, and correct answer
                            data.at[current_question_idx,
                                    'Question'] = question
                            data.at[current_question_idx,
                                    'Choice 1'] = edited_choices[0]
                            data.at[current_question_idx,
                                    'Choice 2'] = edited_choices[1]
                            data.at[current_question_idx,
                                    'Choice 3'] = edited_choices[2]
                            data.at[current_question_idx,
                                    'Choice 4'] = edited_choices[3]
                            data.at[current_question_idx,
                                    'Choice 5'] = edited_choices[4]
                            data.at[current_question_idx,
                                    'Choice 6'] = edited_choices[5]
                            data.at[current_question_idx,
                                    'Right Answer'] = correct_answer
                            data.at[current_question_idx,
                                    'Question Type'] = question_type

                            # Drop the "Choice 0" column if it exists
                            if 'Choice 0' in data.columns:
                                data = data.drop(columns=['Choice 0'])

                            # Set a session state variable to indicate successful saving
                            st.session_state["saving_successful"] = True
                        except Exception as e:
                            st.error(f"حدث خطأ: {str(e)}")
                            st.session_state["saving_successful"] = False

                        # Save all changes to the Excel file
                        save_changes_to_excel(data, selected_file_path)

                    # Change button color to faded green when saving is successful
                    if st.session_state.get("saving_successful"):
                        st.markdown("""
                        <style>
                            .save-button.saved {
                                background-color: #8BC34A !important; /* Faded green when saved */
                            }
                        </style>
                        """, unsafe_allow_html=True)

                    if col3.button("السؤال التالي") and current_question_idx < len(data) - 1:
                        with st.spinner("جاري التحميل..."):
                            current_question_idx += 1
                            st.session_state["current_question_idx"] = current_question_idx

                    if current_question_idx == len(data) - 1:
                        st.markdown(
                            "<div class='header'>نهاية الأسئلة.</div>", unsafe_allow_html=True)

            # Initially display the questions page if an Excel file is uploaded
            page2(data)

        except pd.errors.EmptyDataError:
            st.error("الملف المُرفق فارغ. يرجى تحميل ملف يحتوي على بيانات.")
        except pd.errors.ParserError:
            st.error(
                "حدث خطأ أثناء تحليل ملف الإكسل. يرجى التأكد من أنه ملف إكسل صالح.")
        except Exception as e:
            st.error(f"حدث خطأ: {str(e)}")

    # Display the selected file and edit its content
    edit_selected_file()

else:
    st.sidebar.info("لا توجد ملفات .xlsx في مجلد 'Quizzes Editor'.")
