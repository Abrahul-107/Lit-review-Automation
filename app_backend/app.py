from flask import Flask, request, jsonify # type: ignore
import pandas as pd # type: ignore
import time
from ResearchPaperAccess.arxiv_dataset_access import search_by_title
from llmCalls.llama_ratings import get_rating
from llmCalls.llama_call_for_keyword import get_keyword_from_userquery
from llmCalls.llama_call_for_heading import get_headings_from_llm
from DownloadResearchPaper.get_papers import download_research_paper
from RAG.create_database import generate_data_store
from temp_pdf_to_txt import pdf_to_txt

app = Flask(__name__)

# Store session-like data
data_store = {
    "all_data": pd.DataFrame(),
    "accepted_papers": []
}

folder_name = None
keywords = None

@app.route('/search', methods=['POST'])
def search():
    try:
        global keywords
        data = request.json
        description = data.get("description")
        if description:
            keywords = get_keyword_from_userquery(description)
        else:
            keywords = data.get("keywords")

        if not keywords:
            return jsonify({"error": "Please provide keywords for search."}), 400

        ar_responses = search_by_title(keywords)
        ratings = get_rating(ar_responses)

        data_list = []
        for idx, response in enumerate(ar_responses):
            paper_id = int(time.time()) + idx  # Unique ID
            data_list.append({
                "id": paper_id,
                "Title": response.title,
                "URL": response.pdf_url,
                "Published": response.published,
                "Rating": ratings.get(response.pdf_url, "N/A")
            })

        data_store["all_data"] = pd.DataFrame(data_list)
        return jsonify({"papers": data_list})
    except Exception as e:
        return jsonify({"Error":e})


@app.route('/accept', methods=['POST'])
def accept_papers():
    global folder_name
    data = request.json
    paper_ids = data.get("ids")  # Expecting a list of IDs

    if not paper_ids or not isinstance(paper_ids, list):
        return jsonify({"error": "Please provide a list of paper IDs to accept."}), 400

    print("All Papers Data:\n", data_store["all_data"])

    # Filter papers with matching IDs
    papers = data_store["all_data"][data_store["all_data"]["id"].isin(paper_ids)]

    if papers.empty:
        return jsonify({"error": "No valid paper IDs found."}), 404

    accepted = []
    skipped = []

    for _, row in papers.iterrows():
        paper = row.to_dict()
        if paper not in data_store["accepted_papers"]:
            data_store["accepted_papers"].append(paper)
            accepted.append(paper)
        else:
            skipped.append(paper["id"])

    folder_name = download_research_paper(accepted)

    return jsonify({
        "message": f"{len(accepted)} papers accepted.",
        "accepted_papers": accepted,
        "skipped_ids": skipped
    })

@app.route("/get_headings_rag", methods=['POST'])
def get_headings():
    if not folder_name:
        return jsonify({"Please Accept Ids or give Description to get the headings."}), 405

    # Do PDF to txt first
    pdf_to_txt(folder_name)

    # Create Vector DB from txt folder
    generate_data_store()


@app.route("/get_headings", methods=["POST"])
def get_headings_llm():
    global folder_name, keywords
    if not folder_name:
        return jsonify({"Please Accept Ids or give Description to get the headings."}), 405

    # Do PDF to txt first
    txt_folder = pdf_to_txt(folder_name)

    # Ask LLM to give the headings
    headings = get_headings_from_llm(txt_folder, keywords)
    return jsonify({"headings": headings})


@app.route('/accepted_titles', methods=['GET'])
def get_accepted_titles():
    return jsonify({"accepted_papers": data_store["accepted_papers"]})

if __name__ == '__main__':
    app.run(debug=True)
