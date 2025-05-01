from together import Together  # type: ignore
import os
from dotenv import load_dotenv  # type: ignore
import json
import time

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API key is missing. Set the API_KEY environment variable.")

# LLM Model
model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

# Initialize Together client
client = Together(api_key=api_key)

def call_llm_for_subsection(topic: str, section_title: str, subsection_title: str, pages: int) -> str:
    """
    Calls the Together LLM to generate content for a given subsection.
    Each subsection aims to generate ~500 words per page.
    """
    prompt = f"""
You are an academic research assistant. Write an in-depth literature review section for a research paper titled: "{topic}".

Section: "{section_title}"
Subsection: "{subsection_title}"
Target length: approximately {pages * 500} words.

Guidelines:
- Use formal academic tone.
- Include citations in [Author, Year] format (you can make them up if needed).
- Provide deep insights, examples, theories, frameworks, or real-world applications where relevant.
- Do not repeat content or state generic facts; be specific and scholarly.

Begin now.
"""

    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=8192,
    )

    return response.choices[0].message.content.strip()

def generate_full_literature_review(headings_json: dict) -> str:
    """
    Iterates over all sections and subsections, calling the LLM for each,
    and returns the aggregated content as a single string.
    """
    topic = headings_json["title"]
    full_review = f"# {topic}\n\n"

    for section in headings_json["sections"]:
        section_title = section["heading"]
        full_review += f"\n\n## {section_title}\n"

        for subsection in section.get("subsections", []):
            subsection_title = subsection["subheading"]
            pages = subsection["pages"]
            print(f"Generating content for: {subsection_title} ({pages} pages)")

            try:
                content = call_llm_for_subsection(topic, section_title, subsection_title, pages)
                full_review += f"\n\n### {subsection_title}\n{content}\n"
            except Exception as e:
                print(f"Error generating content for {subsection_title}: {e}")
                full_review += f"\n\n### {subsection_title}\n[Error generating content]\n"

            time.sleep(1.5)  # Respect rate limits

    return full_review

# -------------------------------
# HEADINGS JSON INPUT
# -------------------------------
input = '''{
    "headings": {
        "sections": [
            {
                "heading": "1. Introduction to Machine Learning in Healthcare",
                "pages": 5,
                "subsections": [
                    {
                        "pages": 2,
                        "subheading": "1.1 Background and Motivation"
                    },
                    {
                        "pages": 3,
                        "subheading": "1.2 Scope and Objectives"
                    }
                ]
            },
            {
                "heading": "2. Theoretical Foundations of Machine Learning",
                "pages": 10,
                "subsections": [
                    {
                        "pages": 3,
                        "subheading": "2.1 Supervised and Unsupervised Learning"
                    },
                    {
                        "pages": 4,
                        "subheading": "2.2 Deep Learning and Neural Networks"
                    },
                    {
                        "pages": 3,
                        "subheading": "2.3 Fairness and Bias in Machine Learning"
                    }
                ]
            },
            {
                "heading": "3. Machine Learning Applications in Healthcare",
                "pages": 15,
                "subsections": [
                    {
                        "pages": 5,
                        "subheading": "3.1 Disease Diagnosis and Prediction"
                    },
                    {
                        "pages": 4,
                        "subheading": "3.2 Personalized Medicine and Treatment"
                    },
                    {
                        "pages": 6,
                        "subheading": "3.3 Medical Imaging and Computer Vision"
                    }
                ]
            },
            {
                "heading": "4. Methodological Frameworks for Machine Learning in Healthcare",
                "pages": 12,
                "subsections": [
                    {
                        "pages": 4,
                        "subheading": "4.1 Data Preprocessing and Feature Engineering"
                    },
                    {
                        "pages": 4,
                        "subheading": "4.2 Model Selection and Hyperparameter Tuning"
                    },
                    {
                        "pages": 4,
                        "subheading": "4.3 Evaluation Metrics and Model Validation"
                    }
                ]
            },
            {
                "heading": "5. Challenges and Limitations of Machine Learning in Healthcare",
                "pages": 8,
                "subsections": [
                    {
                        "pages": 3,
                        "subheading": "5.1 Data Quality and Availability"
                    },
                    {
                        "pages": 3,
                        "subheading": "5.2 Regulatory and Ethical Considerations"
                    },
                    {
                        "pages": 2,
                        "subheading": "5.3 Interpretability and Explainability"
                    }
                ]
            },
            {
                "heading": "6. Comparative Studies and Future Directions",
                "pages": 10,
                "subsections": [
                    {
                        "pages": 4,
                        "subheading": "6.1 Comparison of Machine Learning Algorithms"
                    },
                    {
                        "pages": 6,
                        "subheading": "6.2 Future Research Directions and Open Problems"
                    }
                ]
            },
            {
                "heading": "7. Conclusion and Recommendations",
                "pages": 5,
                "subsections": [
                    {
                        "pages": 2,
                        "subheading": "7.1 Summary of Key Findings"
                    },
                    {
                        "pages": 3,
                        "subheading": "7.2 Implications for Practice and Research"
                    }
                ]
            }
        ],
        "title": "Literature Review on Machine Learning in Healthcare",
        "total_pages": 65
    }
}'''

# -------------------------------
# MAIN EXECUTION
# -------------------------------
if __name__ == "__main__":
    headings_json = json.loads(input)["headings"]
    review_text = generate_full_literature_review(headings_json)

    # Save to file
    with open("literature_review.txt", "w", encoding="utf-8") as f:
        f.write(review_text)

    print("Literature review generation complete and saved to 'literature_review.txt'.")
