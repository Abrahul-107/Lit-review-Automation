from together import Together
import os


api_key = '8f9e2a288a3ae3c4742f5b459fec8e8c96bd5464803a55b555d91d9a59aac9f2'

# Ensure API key is provided
if not api_key:
    raise ValueError("API key is missing. Set the TOGETHER_API_KEY environment variable.")

# Initialize the client with the API key
client = Together(api_key=api_key)

# Define model (ensure it exists on Together API)
model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

# Message content (Ensuring UTF-8 encoding is used)
message_content = """
### SEARCH SORTED BY RELEVANCE ###
Title: Deep Learning
Authors: Nicholas G. Polson, Vadim O. Sokolov
Published: 2018-07-20 18:20:34+00:00
Updated: 2018-08-03 11:27:28+00:00
PDF: http://arxiv.org/pdf/1807.07987v2

Title: Deep Learning by Scattering
Authors: Stéphane Mallat, Irène Waldspurger
Published: 2013-06-24 07:52:45+00:00
Updated: 2015-06-25 17:26:01+00:00
PDF: http://arxiv.org/pdf/1306.5532v2

Title: Quantum Deep Learning
Authors: Nathan Wiebe, Ashish Kapoor, Krysta M. Svore
Published: 2014-12-10 23:05:16+00:00
Updated: 2015-05-22 00:20:28+00:00
PDF: http://arxiv.org/pdf/1412.3489v2

Title: Deep Learning in Finance
Authors: J. B. Heaton, N. G. Polson, J. H. Witte
Published: 2016-02-21 18:19:56+00:00
Updated: 2018-01-14 13:19:20+00:00
PDF: http://arxiv.org/pdf/1602.06561v3

Title: Deep Learning in Bioinformatics
Authors: Seonwoo Min, Byunghan Lee, Sungroh Yoon
Published: 2016-03-21 13:55:02+00:00
Updated: 2016-06-19 09:16:30+00:00
PDF: http://arxiv.org/pdf/1603.06430v5

Search time (title - Relevance): 8.30 seconds
...
Provide the output in proper JSON format, with the PDF title as the key and the remaining information as values. Additionally, include a rating for each paper out of 10. Only provide the JSON output, without any explanations.
"""

# Make the API call
response = client.chat.completions.create(
    model=model_name,
    messages=[{"role": "user", "content": message_content}],
    max_tokens=1024  #
)

# Print the response
print(response.choices[0].message.content)
