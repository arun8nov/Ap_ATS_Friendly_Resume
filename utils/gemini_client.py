import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

def get_gemini_response(prompt: str) -> str:
    """Takes a prompt string, returns the response text from NVIDIA API."""
    try:
        completion = client.chat.completions.create(
            model="google/gemma-2-27b-it",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            top_p=0.7,
            max_tokens=4096,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return "Error from NVIDIA API: " + str(e)
