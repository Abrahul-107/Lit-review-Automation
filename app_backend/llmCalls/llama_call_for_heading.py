from together import Together  # type: ignore
import os
from dotenv import load_dotenv  # type: ignore
import json
from json_repair import repair_json
# Load environment variables from .env
load_dotenv()

# Retrieve API key
api_key = os.getenv("API_KEY")

# Ensure API key is set
if not api_key:
    raise ValueError("API key is missing. Set the API_KEY environment variable.")

# Define the LLM model to use
model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo"


import json

def clean_and_format_json(raw_response: str) -> dict:
    """
    Cleans and formats the raw JSON string returned by the LLM into a valid JSON object.
    """
    try:
        # Remove the leading '```json' and trailing '```' if present, and extra newline/escape characters
        if raw_response.startswith("```json"):
            raw_response = raw_response.strip("` \n").replace("```json", "").replace("```", "").strip()

        # Parse the cleaned string into a Python dict
        parsed_json = json.loads(raw_response)

        # Pretty print to console (optional)
        formatted_json = json.dumps(parsed_json, indent=4)
        print(formatted_json)

        return parsed_json

    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        raise


def read_all_txt(folder_path: str) -> str:
    """
    Reads all .txt files from a folder and aggregates their content.
    Each file's content is prefixed by a header indicating the filename.
    """
    all_text = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                text = f.read()
                all_text += f"\n\n--- Content from {filename} ---\n{text}"
    return all_text
def get_headings_from_llm(txt_folder: str, keywords: str) -> dict:
    """
    Uses the Together API to generate a structured outline for a literature review paper.
    Returns a valid Python dictionary parsed from the LLM's JSON response.
    """
    print("Keyword:", keywords)

    client = Together(api_key=api_key)
    context = read_all_txt(txt_folder)

    prompt_template = f"""
You are a research assistant specializing in {keywords}.

Using the provided content from multiple academic and research texts, generate a structured and academically rigorous outline for a literature review paper on the topic: {keywords}.

Requirements:

1. Section Headings:  
   Generate a numbered list of major section headings that reflect the core themes, techniques, challenges, theoretical foundations, applications, and insights found in the source material. Section titles should be concise yet descriptive, similar in style to those used in top-tier {keywords} conference and journal papers.

2. Complete Outline:  
   Produce a detailed outline for a 60–70 page literature review, including:
   - 6 to 8 major sections (headings)
   - Multiple subheadings under each main section (depth of 2–3 levels where appropriate)
   - Each section and subsection should have an estimated page count, with the total across all sections summing to between 60 and 70 pages.
   - Ensure a balanced distribution across:
     - Theoretical foundations  
     - Practical implementations  
     - Methodological frameworks  
     - gap analyis 
     - theoretical framework 
     - Applications and use cases  
     - Challenges and limitations  
     - Comparative studies  
     - Future directions and open problems

3. Output Format:  
   The final output should be in JSON format, with the following structure:
   {{
     "title": "Literature Review on {keywords}",
     "total_pages": XX,
     "sections": [
       {{
         "heading": "1. Section Title",
         "pages": X,
         "subsections": [
           {{
             "subheading": "1.1 Subsection Title",
             "pages": X
           }},
           ...
         ]
       }},
       ...
     ]
   }}

4. Tone and Style:  
   Use formal academic language suitable for peer-reviewed publication or thesis submission. Ensure headings are logically organized, non-overlapping, and conducive to deep exploration.
    Don't give any other explanation just give me the json only nothing else
Text Content:
{context}
"""

    # Call the LLM
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt_template}],
        max_tokens=4096,
    )

    # Extract the content string
    raw_response = response.choices[0].message.content.strip()

    # Step 1: Clean off backticks and ```json if present
    if raw_response.startswith("```json") or raw_response.startswith("```"):
        raw_response = raw_response.strip("` \n").replace("```json", "").replace("```", "").strip()

    try:
        # Step 2: Try direct load
        parsed_json = json.loads(raw_response)
    except json.JSONDecodeError:
        # Step 3: Fallback to json repair
        repaired = repair_json(raw_response)
        parsed_json = json.loads(repaired)

    return parsed_json
