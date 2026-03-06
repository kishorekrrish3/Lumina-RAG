import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# The genai.Client() will automatically look for GEMINI_API_KEY in the environment
client = genai.Client()

def generate_answer(query, contexts):

    context_text = "\n\n".join(contexts)

    prompt = f"""
You are an AI research assistant.

Use the provided research paper context to answer the question.

If the context does not contain enough information, say that clearly.

Context:
{context_text}

Question:
{query}

Answer clearly and concisely.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text