# quiz_generator.py

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load OpenAI key
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(api_key=openai_key, temperature=0.7)

def generate_mcqs(text_chunk: str, num_questions=3):
    """
    Generate multiple-choice questions from a given text chunk using GPT.
    """
    prompt = f"""
You are an educational assistant. Based on the following study content, generate {num_questions} multiple-choice questions. 
Each question must have 4 options (A, B, C, D) and clearly indicate the correct answer.

Text:
{text_chunk}

Format your response exactly like this:
Q1. [Question here]
A. ...
B. ...
C. ...
D. ...
Answer: A

Q2. ...
    """

    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"❌ Failed to generate questions: {e}"
