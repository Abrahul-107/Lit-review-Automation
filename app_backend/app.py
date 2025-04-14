from flask import Flask, request, jsonify
import pandas as pd
import time
from ResearchPaperAccess.arxiv_dataset_access import search_by_title
from llmCalls.llama_ratings import get_rating

app = Flask(__name__)

# Store session-like data
data_store = {
    "all_data": pd.DataFrame(),
    "accepted_papers": []
}

@app.route('/search', methods=['POST'])
def search():
    data = request.json
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

@app.route('/accept', methods=['POST'])
def accept_papers():
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

    return jsonify({
        "message": f"{len(accepted)} papers accepted.",
        "accepted_papers": accepted,
        "skipped_ids": skipped
    })


@app.route('/accepted_titles', methods=['GET'])
def get_accepted_titles():
    return jsonify({"accepted_papers": data_store["accepted_papers"]})

if __name__ == '__main__':
    app.run(debug=True)
