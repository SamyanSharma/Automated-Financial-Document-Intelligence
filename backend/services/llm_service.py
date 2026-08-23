import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

model_name = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is missing from .env"
    )


client = genai.Client(
    api_key=api_key
)



def generate_answer(
    question: str,
    context: str
) -> str:


    prompt = f"""

You are a financial document analysis assistant.

Answer the question ONLY using the provided document context.

Rules:
1. Do not invent financial numbers.
2. Do not use information outside the context.
3. If information is missing, say clearly.
4. Mention source chunk IDs.

QUESTION:

{question}


DOCUMENT CONTEXT:

{context}

"""


    response = client.interactions.create(
        model=model_name,
        input=prompt
    )


    return response.output_text
def generate_json(
    prompt: str
) -> str:


    response = client.interactions.create(
        model=model_name,
        input=prompt
    )


    return response.output_text