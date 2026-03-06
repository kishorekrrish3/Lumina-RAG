import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()

def expand_query(query):
    try:
        prompt = f"""Generate 3 alternative search queries for: {query}

Return only the queries, one per line, no numbering or bullet points."""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        lines = [line.strip() for line in response.text.strip().split("\n") if line.strip()]
        return lines[:3]

    except Exception as e:
        print(f"Query expansion failed (non-critical): {e}")
        return []