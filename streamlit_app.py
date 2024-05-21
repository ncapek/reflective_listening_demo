from datetime import datetime, timedelta

import openai
import streamlit as st

from classes import ConversationBuilder, LLMAgent
from config import MAX_CALLS_PER_DAY, MAX_MESSAGES
from mongodb_manager import MongoPersistence

openai.api_key = st.secrets["OPENAI_KEY"]

# Initialize the LLMAgent
llm_agent = LLMAgent()

RESET_INTERVAL = timedelta(days=1)  # 24-hour interval


# Check if the API call limit has been reached
def check_limit():
    if "api_calls" not in st.session_state:
        st.session_state["api_calls"] = 0
        st.session_state["last_reset"] = datetime.now()

    time_since_reset = datetime.now() - st.session_state["last_reset"]
    if time_since_reset > RESET_INTERVAL:
        st.session_state["api_calls"] = 0
        st.session_state["last_reset"] = datetime.now()

    if st.session_state["api_calls"] >= MAX_CALLS_PER_DAY:
        return False
    return True


# Increment the count of API calls
def increment_call_count():
    st.session_state["api_calls"] += 1


# Title and instructions
st.title("Reflective Listening Practice Chatbot")
st.write(
    """
This app is designed to help you practice your reflective listening skills. 
You will chat with an automated agent that responds based on your inputs. 
Try to engage in meaningful conversation and watch how the agent reacts to your style of communication.
You are limited to a maximum conversation length of 20 messages, after which you will be given an evaluation and the true intentions of the chatbot will be revealed.
"""
)

# Initialize the conversation using ConversationBuilder
if "conversation" not in st.session_state:
    builder = ConversationBuilder()
    st.session_state["conversation"] = builder.build()

# Display user visible context
st.write(
    f"Conversation Context: {st.session_state['conversation'].user_visible_context}"
)


# Initialize or restart the conversation
def init_conversation():
    builder = ConversationBuilder()
    st.session_state["conversation"] = builder.build()


if "conversation" not in st.session_state:
    init_conversation()


def handle_message():
    if not check_limit():
        st.error(
            "The maximal number of daily messages has been reached. Please try again tomorrow."
        )
        return
    user_message = st.session_state.user_input
    if user_message:  # if the message is not empty
        conversation = st.session_state["conversation"]
        conversation.add_message(user_message)
        st.session_state.user_input = (
            ""  # Clear the input box after sending the message
        )

        # Generate LLM response
        llm_response = llm_agent.generate_response(
            conversation, model="gpt-4-turbo", temperature=0.5
        )
        conversation.add_message(llm_response)
    increment_call_count()  # Increment the call count after a successful API call


# Create a text input for the user message, with a key that matches the session_state key
user_input = st.text_input("Write your messages here", key="user_input")
send_button = st.button("Send", on_click=handle_message)

# Display the conversation
conversation = st.session_state["conversation"]
conversation_text = conversation.format_messages_for_prompt()
num_lines = conversation_text.count("\n") + 1
text_area_height = 600
st.text_area(
    "Conversation",
    conversation_text,
    height=text_area_height,
    key="conversation_display",
)

if conversation.finished:
    if "logged" not in st.session_state:
        persistence_manager = MongoPersistence(st.secrets["MONGO_CONNECTION_STRING"])
        persistence_manager.save_conversation(conversation)
        st.session_state["logged"] = True  # Set the flag to prevent re-logging

    st.subheader("True Context of the Conversation")
    st.write(conversation.context)

    if "evaluation" not in st.session_state:
        evaluation = llm_agent.evaluate_conversation(conversation, "gpt-4-turbo", 0.5)
        conversation.evaluation = evaluation
        st.session_state["evaluation"] = (
            evaluation  # Save evaluation to prevent re-computation
        )

    st.subheader("Evaluation of Your Reflective Listening Skills:")
    st.write(st.session_state["evaluation"])
    st.subheader("To start a new conversation, please refresh the page.")
