import requests
import streamlit as st

MODEL = "gemma4:e2b"
OLLAMA_URL = "http://localhost:11434/api/chat"

st.set_page_config(
    page_title="StudyBuddy",
    layout="centered",
)

st.title("Mr Smarty Pants AI")
st.caption("Your personal AI study assistant, powered by Gemma 4.")

st.write(
    "Paste your class notes below. Mr Smarty Pants AI will help you "
    "understand them, memorize them, or test your knowledge."
)

subject = st.selectbox(
    "What subject are you studying?",
    [
        "Biology",
        "Physics",
        "Chemistry",
        "History",
        "Mathematics",
        "Computer Science",
        "English",
        "Other",
    ],
)

mode = st.radio(
    "What would you like to do?",
    ["Explain my notes", "Make flashcards", "Create a quiz"],
)

notes = st.text_area(
    "Your class notes",
    placeholder="Paste your notes here...",
    height=220,
)

def make_prompt(subject, mode, notes):
    if mode == "Explain my notes":
        task = """
        Explain these notes to a high school student.
        Start with the main idea, explain difficult terms,
        and give a simple example where useful.
        Finish with three important takeaways.
        """

    elif mode == "Make flashcards":
        task = """
        Create 8 useful question-and-answer flashcards.
        Number each card. Label the question FRONT and
        the answer BACK. Keep answers concise and specific.
        """

    else:
        task = """
        Create 5 multiple-choice questions based on the notes.
        Give each question four options labelled A, B, C, D.
        Put the answer key and a short explanation at the end.
        Do not reveal answers alongside the questions.
        """

    return f"""
    You are Mr Smarty Pants, a helpful and patient tutor. You use humor and analogies to explain complex topics.

    Subject: {subject}

    IMPORTANT RULES:
    - Treat the student's notes as your main souarce.
    - Do not invent facts or pretend the notes cover something
      they do not cover.
    - If you add outside knowledge, clearly label it.
    - Explain concepts at a high school level.
    - Use readable headings and formatting.
    - Be funny and likeable.

    TASK:
    {task}

    STUDENT NOTES:
    {notes}
    """

if st.button("Generate study material", type="primary"):
    if not notes.strip():
        st.warning("Paste some class notes first.")

    else:
        prompt = make_prompt(subject, mode, notes)

        with st.spinner("Mr smarty pants is working..."):
            try:
                response = requests.post(
                    OLLAMA_URL,
                    json={
                        "model": MODEL,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                        "stream": False,
                    },
                    timeout=300,
                )

                response.raise_for_status()

                answer = response.json()["message"]["content"]
                st.session_state["answer"] = answer

            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to Ollama. "
                    "Open Ollama and make sure it is running."
                )

            except requests.exceptions.Timeout:
                st.error(
                    "The model took too long to respond. "
                    "Try shorter notes or a smaller model."
                )

            except requests.exceptions.RequestException as error:
                st.error(f"Ollama returned an error: {error}")

if "answer" in st.session_state:
    st.divider()
    st.subheader("Your study material")
    st.markdown(st.session_state["answer"])


