import streamlit as st
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools import DuckDuckGoSearchRun
import data
from voice import transcribe, text_to_speech
from webscrap import ws
from graphs import graph_generator
from mailsender import send_email
from mailsender import create_event
import re
import pandas as pd
from dotenv import load_dotenv
import os
import requests


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")


# ============================================================
# LLM
# ============================================================

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=groq_api_key
)


# ============================================================
# RAG CHAIN
# ============================================================

custom_prompt = ChatPromptTemplate.from_template("""
You are a helpful gardening assistant.

Use ONLY the relevant information from the following context
to answer the user's question.

If the answer is not in the context, say:
"I don't know."

Context:
{context}

Question:
{input}

Answer:
""")


if "rag_chain" not in st.session_state:

    retriever = data.vector_store.as_retriever()

    rag_chain = (
        {
            "context": retriever,
            "input": RunnablePassthrough()
        }
        | custom_prompt
        | llm
        | StrOutputParser()
    )


# ============================================================
# TOOLS
# ============================================================

@tool
def get_weather(city: str) -> str:
    """
    Use this tool only when the user asks about the current
    weather, temperature, rainfall, or forecast for a city.
    """

    url = (
        f"https://api.weatherapi.com/v1/current.json"
        f"?key={weather_api_key}&q={city}"
    )

    response = requests.get(url)
    weather_data = response.json()

    return (
        f"The current temperature in {city} is "
        f"{weather_data['current']['temp_c']}°C "
        f"with {weather_data['current']['condition']['text']}."
    )


@tool
def rag_tool(query: str) -> str:
    """
    Use this tool first for any gardening or plant-related
    question.

    It searches the internal gardening documents for the answer.
    """

    return rag_chain.invoke(query)


@tool
def qa_tool(question: str) -> str:
    """
    Use this tool for all other questions or when the gardening
    documents do not contain the required information.

    It searches the internet.
    """

    search = DuckDuckGoSearchRun()

    return search.invoke(question)


@tool
def send_email_input_string(input_string: str):
    """
    Send an email.

    Format:
    to: <email>, subject: <subject>, message: <message>
    """

    try:

        to_match = re.search(
            r"to:\s*(.*?)(?=, subject:|$)",
            input_string,
            re.IGNORECASE
        )

        subject_match = re.search(
            r"subject:\s*(.*?)(?=, message:|$)",
            input_string,
            re.IGNORECASE
        )

        message_match = re.search(
            r"message:\s*(.*)",
            input_string,
            re.IGNORECASE | re.DOTALL
        )

        to = to_match.group(1).strip() if to_match else None
        subject = (
            subject_match.group(1).strip()
            if subject_match else None
        )
        message = (
            message_match.group(1).strip()
            if message_match else None
        )

        if to and subject and message:

            return send_email(
                to,
                subject,
                message
            )

        else:

            return "Error: Missing to, subject, or message."

    except Exception as e:

        return f"Error parsing input: {str(e)}"


@tool
def schedule_meeting_input_string(input_string: str):
    """
    Schedule a gardening meeting.

    Input format:
    title: Gardening Talk,
    description: Discuss soil health,
    start_time: 2025-04-10T15:30:00,
    duration: 45
    """

    try:

        parts = input_string.split(",")

        title = parts[0].split("title:")[1].strip()

        description = (
            parts[1].split("description:")[1].strip()
        )

        start_time = (
            parts[2].split("start_time:")[1].strip()
        )

        duration = int(
            parts[3]
            .split("duration:")[1]
            .strip()
            .replace("'", "")
        )

        return create_event(
            title,
            description,
            start_time,
            duration
        )

    except Exception as e:

        return f"Error parsing meeting input: {str(e)}"


# ============================================================
# TOOLS LIST
# ============================================================

tools = [
    get_weather,
    rag_tool,
    qa_tool,
    send_email_input_string,
    schedule_meeting_input_string
]


# ============================================================
# CONVERSATION MEMORY
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# AGENT
# ============================================================

if "agent" not in st.session_state:

    custome_prompt = """
You are ProBot, a helpful gardening assistant.

You help users with:

- Gardening
- Plant care
- Pest control
- Composting
- Soil
- Fertilizers
- Plant diseases
- Weather
- General questions
- Emails
- Meetings

IMPORTANT CONVERSATION MEMORY RULE:

You will receive the complete conversation history.

Use previous messages to understand references such as:

- "it"
- "this plant"
- "that"
- "my plant"
- "the problem"
- "how often should I water it?"
- "what about fertilizer?"
- "tell me more"
- "as I said earlier"

Remember information the user has already provided during
this conversation.

For gardening questions:

1. Use RAGTool first.
2. If RAGTool responds with "I don't know", use QA_Tool.

For weather questions:

Use the Weather tool.

For emails:

Once you have enough information, use the EmailSender tool.

When writing an email, never include my name/signature unless
the user explicitly provides one.

For meetings:

Use the meeting tool when the user asks to schedule a meeting.

Be friendly, concise, and informative.
"""


    st.session_state.agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=custome_prompt
    )


# ============================================================
# STREAMLIT UI
# ============================================================

st.set_page_config(
    page_title="ProBot",
    layout="wide"
)

st.title("🌱 ProBot")


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("ProBot Settings")


# Clear conversation button

if st.sidebar.button("🗑️ Clear Conversation"):

    st.session_state.messages = []

    st.rerun()


# Communication mode

user_select = st.sidebar.selectbox(
    "How would you like to communicate?",
    ("Text", "Voice")
)


# ============================================================
# DISPLAY OLD CONVERSATION
# ============================================================

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        if msg.get("type") == "image":

            st.image(
                msg["content"],
                caption=msg["content"]
            )

        else:

            st.markdown(msg["content"])


# ============================================================
# VISUALIZATION
# ============================================================

st.sidebar.subheader("Upload for Visualization")

file = st.sidebar.file_uploader(
    "Upload CSV or Excel",
    type=["csv", "xlsx"]
)


if file and st.sidebar.button("Generate Charts"):

    try:

        if file.name.endswith(".csv"):

            df = pd.read_csv(file)

        else:

            df = pd.read_excel(file)

        if df.empty:

            st.warning("Uploaded file is empty.")

        else:

            with st.spinner("Generating charts..."):

                images = graph_generator(df)

            if not images:

                st.error("Couldn't generate charts.")

            else:

                for img in images:

                    st.image(
                        img,
                        use_container_width=True
                    )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "type": "image",
                            "content": img,
                        }
                    )

    except Exception as e:

        st.error(str(e))


# ============================================================
# FUNCTION TO RUN AGENT WITH MEMORY
# ============================================================

def run_agent(user_input):

    # --------------------------------------------------------
    # Add user's message to memory
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # --------------------------------------------------------
    # Convert Streamlit messages to LangChain messages
    # --------------------------------------------------------

    conversation = []

    for msg in st.session_state.messages:

        # Ignore images
        if msg.get("type") == "image":
            continue

        role = msg["role"]
        content = msg["content"]

        conversation.append(
            (role, content)
        )

    # --------------------------------------------------------
    # Send ENTIRE conversation to the agent
    # --------------------------------------------------------

    response = st.session_state.agent.invoke(
        {
            "messages": conversation
        }
    )

    # --------------------------------------------------------
    # Get final answer
    # --------------------------------------------------------

    ai_answer = response["messages"][-1].content

    # --------------------------------------------------------
    # Save assistant answer
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": ai_answer
        }
    )

    return ai_answer


# ============================================================
# TEXT CHAT
# ============================================================

if user_select == "Text":

    if prompt := st.chat_input("Ask Anything....."):

        with st.chat_message("user"):

            st.markdown(prompt)

        with st.chat_message("assistant"):

            with st.spinner("Thinking....."):

                ai_answer = run_agent(prompt)

                st.markdown(ai_answer)


# ============================================================
# VOICE CHAT
# ============================================================

else:

    uploaded_file = st.audio_input(
        "Record a Voice Message"
    )

    if uploaded_file and st.button("🎤 Confirm Audio"):

        user_input = transcribe(uploaded_file)

        if user_input:

            # Show user message

            with st.chat_message("user"):

                st.markdown(user_input)

            # Run agent

            with st.chat_message("assistant"):

                with st.spinner("Thinking..."):

                    ai_answer = run_agent(user_input)

                    if ai_answer.strip():

                        audio_file = text_to_speech(
                            ai_answer,
                            "en"
                        )

                        st.sidebar.audio(
                            audio_file,
                            format="audio/mp3",
                            autoplay=True
                        )

                    st.markdown(ai_answer)

