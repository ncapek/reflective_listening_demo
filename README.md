
# Reflective listening practice chatbot!

This project combines my love for AI and listening skills, taught by Dr. K. from HealthyGamerGG.

## Background: Not long ago, I took a Udemy course on active listening (as well as a lot of material from Dr. K.), and it really transformed my approach to conversations. It was eye-opening to see how actively engaging in listening can profoundly impact how conversations turn out. I’ve been using these skills and found that it has a major impact on how people feel and often helps them figure out their current problems. It also made me realize that a whole lot of people feel really lonely because they don't have anyone to actually listen to them.

## The Project: Inspired by this, I decided investigate if we can use AI to help people build their listening skills so they can have more meaningful interactions. The result is a Reflective Listening Practice Chatbot prototype, which I intend to build on further.

## Tech Stack:

Streamlit: For the frontend to quickly design and deploy.
MongoDB Atlas: For simple data persistence.
OpenAI’s GPT: I'm currently using GPT4 to generate agent responses and conversation evaluations.

## The chatbot helps users practice and enhance their reflective listening skills by engaging in simulated dialogues. The agent has something it wants to share with the user but is careful about approaching the subject. And depending on how the user reacts, the agent decides if it's safe to share its problems.

I’m looking forward to your feedback and thoughts.🌍💬

Notes:
Since I am calling the OpenAI API, I have set an upper limit on the maximum daily conversations, so the app might be down at times.

Project link: https://ncapek-reflective-listening-prototype-streamlit-app-nxuzqe.streamlit.app/

Resources: 
https://www.youtube.com/watch?v=tIATzLf-y04
https://www.teaching.unsw.edu.au/group-work-reflective-listening

Next steps:
Build a web (FE in svelte.js, BE in fastapi)
Experiment with different LLM models and parameters
Categorize conversation starters based on topic and let user choose
Implement online A/B testing to serve the most succesful model/hyperparameter combination
Design a feature extraction pipeline to apply to each conversation
Implement some visualization to find if certain conversation patterns are more effective in getting the agent to open up