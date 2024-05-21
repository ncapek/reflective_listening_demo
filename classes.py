"""
This module serves to develop a prototype demonstrating how a chatbot can provide reasonable responses via a text interface.
"""

import json
import os
import random
from enum import Enum
from typing import List

import openai

from config import INSTRUCTIONS, MAX_MESSAGES, next_message_prompt
from conversation_starters import STARTERS


class Speaker(str, Enum):
    """
    This class determines possible values of the current speaker.
    """

    USER = "USER"
    CHATBOT = "CHATBOT"


class Conversation:
    """
    This class holds all components of a single conversation.
    """

    def __init__(
        self,
        max_messages: int,
        messages: List[str],
        current_speaker: Speaker,
        finished: bool,
        context: str,
        user_visible_context: str,
        num_of_messages_sent_by_agent: int,
    ):
        self.max_messages = max_messages
        self.messages: list[str] = messages
        self.current_speaker: Speaker = current_speaker  # Default starting speaker
        self.finished: bool = finished
        self.context: str = context
        self.user_visible_context: str = user_visible_context
        self.num_of_messages_sent_by_agent = num_of_messages_sent_by_agent
        self.evaluation = None

    def add_message(self, message: str):
        """
        Adds a message to the conversation.
        Args:
            message (str): The message to add.
        """

        if not self.finished:
            self.messages.append(message)
            if self.current_speaker == Speaker.CHATBOT:
                self.num_of_messages_sent_by_agent += 1
            if self.get_remaining_agent_messages() <= 0:
                self.finished = True
            self.switch_speaker()

    def switch_speaker(self):
        """
        Switches the turn to the next speaker. Alternates between USER and CHATBOT.
        """
        self.current_speaker = (
            Speaker.CHATBOT if self.current_speaker == Speaker.USER else Speaker.USER
        )

    def format_messages_for_prompt(self):
        """
        This is a helper function that takes the messages and outputs them in a format that can
        be injected into an LLM prompt.

        Example:
        <Agent>: I was in the store today and I saw a pigeon walking around inside.
        <User>: Wow. Thats crazy.
        <Agent>: Yeah, it was the only fun thing that happened to me in a while.

        """
        formatted_messages = ""
        current_speaker = Speaker.CHATBOT
        for message in self.messages:
            formatted_messages += f"<{current_speaker.name}>: {message}\n"
            current_speaker = (
                Speaker.CHATBOT if current_speaker == Speaker.USER else Speaker.USER
            )
        return formatted_messages

    def get_remaining_agent_messages(self):
        """
        Helper function to get the remaining number of messages the agent should send.
        """
        return self.max_messages / 2.0 - self.num_of_messages_sent_by_agent

    def __str__(self):
        return f"""Current speaker: {self.current_speaker.name},\n
            Total messages: {len(self.messages)},\n
            Message: {self.messages},\n
            User visible context: {self.user_visible_context},\n
            Context: {self.context}"""

    def to_dict(self):
        """
        Convert the conversation instance to a dictionary for serialization.
        """
        return {
            "max_messages": self.max_messages,
            "messages": self.messages,
            "current_speaker": self.current_speaker.name,
            "finished": self.finished,
            "context": self.context,
            "user_visible_context": self.user_visible_context,
            "num_of_messages_sent_by_agent": self.num_of_messages_sent_by_agent,
            "evaluation": self.evaluation,
        }

    @staticmethod
    def from_dict(data: dict):
        """
        Create a conversation instance from a dictionary.
        """
        # conversation = Conversation(data["max_messages"])
        # conversation.messages = data["messages"]
        # conversation.current_speaker = data["current_speaker"]
        # conversation.finished = data["finished"]
        # conversation.context = data["context"]
        # conversation.user_visible_context = data["user_visible_context"]
        # conversation.num_of_messages_sent_by_agent = data["num_of_messages_sent_by_agent"]
        return Conversation(**data)


class ConversationBuilder:
    """
    This class is responsible for building and initializing conversations.
    """

    def build(self) -> Conversation:
        """
        Builds a conversation object.

        Returns:
        Conversation: the built conversation
        """

        chosen_starter = random.choice(STARTERS)
        return Conversation(
            max_messages=MAX_MESSAGES,
            messages=[chosen_starter["initial_message"]],
            current_speaker=Speaker.USER,
            finished=False,
            context=chosen_starter["context"],
            user_visible_context=chosen_starter["user_visible_context"],
            num_of_messages_sent_by_agent=1,
        )


class LLMAgent:

    def generate_response(
        self, conversation: Conversation, model: str, temperature: float
    ):
        """
        Generates a response from the LLM based on the given prompt.

        Args:
            conv (Conversation): The conversation object holding the conversation.
            model (str): The OpenAI model to be used.
            temperature (float): The temperature of the model.

        Returns:
            str: The generated response from the LLM.
        """
        prompt = next_message_prompt.format(
            instructions=INSTRUCTIONS,
            num_of_remaining_messages=conversation.get_remaining_agent_messages(),
            context=conversation.context,
            conversation=conversation.format_messages_for_prompt(),
        )
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a chatbot designed to help the user practice reflective listening skills.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        return json.loads(response.choices[0].message.content)["agent_response"]

    def evaluate_conversation(
        self, conversation: Conversation, model: str, temperature: float
    ):
        """
        Generates an evaluation of the conversation based on the context and conversation history.

        Args:
            conversation (Conversation): The conversation object to be evalued
            model (str): The OpenAI model to be used.
            temperature (float): The temperature of the model.

        Returns:
            str: The evaluation of the conversation.
        """
        prompt = f"Please write a very short and specific evaluation. The <user> is a human training their reflective listening skills against a chatbot. The chatbot is programmed to open up if the user utilized reflective listening and react neutrally or even hostilely otherwise: Context: {conversation.context} Conversation: {conversation.format_messages_for_prompt()}"
        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "assistant", "content": prompt}],
            temperature=temperature,
            max_tokens=150,
        )
        return response.choices[0].message.content


if __name__ == "__main__":
    openai.api_key = os.getenv("OPENAI_KEY")
    conv_builder = ConversationBuilder()
    conv = conv_builder.build()
    llm_agent = LLMAgent()
    print(conv.format_messages_for_prompt())

    while not conv.finished:
        user_message = input("<USER>: ")
        conv.add_message(user_message)
        agent_message = llm_agent.generate_response(conv, "gpt-4-turbo", 0.5)
        # agent_message = generate_message(llm_prompt)
        conv.add_message(agent_message)
        print(f"<CHATBOT>: {agent_message}")

    print(
        f"Evaluation of user: {llm_agent.evaluate_conversation(conv, 'gpt-4-turbo', 0.0)}"
    )
