from together import Together
import os, json
from dotenv import load_dotenv
from json_repair import repair_json

# Load environment variables
load_dotenv()

api_key = os.getenv("API_KEY")

# Ensure API key is provided
if not api_key:
    raise ValueError(
        "API key is missing. Set the TOGETHER_API_KEY environment variable."
    )

# Define model (ensure it exists on Together API)
model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

def get_rating(response):
    client = Together(api_key=api_key)

    prompt = ""
    for result in response:
        formatted_string = f"""Title: {result.title}
            Published: {result.published}
            PDF: {result.pdf_url}"""
        prompt += formatted_string

    # Message content (Ensuring UTF-8 encoding is used)
    message_content = f"Provide the output in proper JSON format, with the PDF title as the key and value is the rating for each paper out of 10. Only provide the JSON output, without any explanations. \n\n{prompt}"

    # Make the API call
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": message_content}],
        max_tokens=1024,  
    )

    # Print the response
    response = repair_json(response.choices[0].message.content)
    print(response)
    return json.loads(response)
