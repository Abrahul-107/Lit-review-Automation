from together import Together  # type: ignore
import os
from dotenv import load_dotenv  # type: ignore

# Load environment variables
load_dotenv()

api_key = os.getenv("API_KEY")

# Ensure API key is provided
if not api_key:
    raise ValueError("API key is missing. Set the API_KEY environment variable.")

# Define model
model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo"


def read_all_txt(folder_path):
    all_text = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                text = f.read()
                all_text += f"\n\n--- Content from {filename} ---\n{text}"
    return all_text


def get_headings_from_llm(txt_folder, keywords):
    print("Keyword",keywords)
    client = Together(api_key=api_key)

    context = read_all_txt(txt_folder)

    # Prepare message
    prompt_template = f"""
        You are a {keywords} research assistant.

        Using the content provided below from several research texts, generate a set of structured and academically meaningful section headings for a new research paper. The headings should reflect core themes, techniques, challenges, and insights found in the material. Each section title should be concise but descriptive, like those used in top-tier {keywords} conference papers.

        Text Content:
        {context}

        Return the output as a numbered list of section titles.
        """

    # Make the API call
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt_template}],
        max_tokens=4096,  # Small since expecting just one word
    )
    print(response)
    print("----------------------------------------------------")
    response = response.choices[0].message.content.strip()

    return response
