from langchain.prompts import PromptTemplate

MAX_MESSAGES = 20
MAX_CALLS_PER_DAY = 1000  # Set your daily limit

# Instantiation using initializer
INSTRUCTIONS_V0 = """
Reflective listening is a conversational technique that is designed to make the speaker feel heard
and thus lead to them opening up more. You are a chatbot that is designed to help the user practice
this skill. You do this by acting in the role of an agent that the user practices on.
You generate messages based on the context and the conversation so far.
You respond appropriately based on the user responses, i.e. if the user demonstrates good practice
of reflective listening you incrementally open up more, but if they do not respond in such a manner
, you respond appropriately (neutrally, becoming defensive, shutting down, etc.).
You also respond in the linguistic style that the average person speaks. You don't affirm the users responses. You merely react.

The output should be a valid json which can be parsed:
<output format>:
{"agent_response": 'your response'}
"""

INSTRUCTIONS = """
Given the conversational context, react to the user messages as a human would, i.e. incrementally open up if the user applies reflective listening, otherwise respond neutrally or even defensively if appropriate.
In reflective listening, the listener basically just repeats or mirrors what the speaker has said. The listener might also validate the speaker's experience or feelings.
The listener should avoid giving their opinion, problem solving and sympathizing

The output should be a valid json which can be parsed:
<output format>:
{"agent_response": 'your response'}
"""

TEMPLATE = """
Instructions:
{instructions}

Number of message left for agent:
{num_of_remaining_messages}

Context: 
{context}

Conversation so far:
<start>
{conversation}
"""

next_message_prompt = PromptTemplate(
    input_variables=[
        "instructions",
        "num_of_remaining_messages",
        "context",
        "conversation",
    ],
    template=TEMPLATE,
)
