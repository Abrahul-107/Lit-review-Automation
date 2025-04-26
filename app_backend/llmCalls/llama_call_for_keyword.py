from together import Together # type: ignore
import os
from dotenv import load_dotenv # type: ignore

# Load environment variables
load_dotenv()

api_key = os.getenv("API_KEY")

# Ensure API key is provided
if not api_key:
    raise ValueError(
        "API key is missing. Set the API_KEY environment variable."
    )

# Define model
model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

def get_keyword_from_userquery(topic: str) -> str:
    client = Together(api_key=api_key)

    # Prepare message
    message_content = (
        f"Extract a short, meaningful phrase (maximum 6 words) that precisely captures the core idea of the topic: \"{topic}\". "
        "Only return the phrase without any extra text, explanation, punctuation, or quotation marks."
    )

    # Make the API call
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": message_content}],
        max_tokens=10,  # Small since expecting just one word
    )

    keyword = response.choices[0].message.content.strip()
    return keyword