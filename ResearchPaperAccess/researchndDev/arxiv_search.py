'''
@author: Debomita Sahoo
date: 18/02/2025
'''

import arxiv
import time

# Initialize arXiv client
client = arxiv.Client()

def arxiv_search(query, search_type="title", max_results=5, sort_by=arxiv.SortCriterion.Relevance):
    """
    Performs a precise search on arXiv with different sorting options.

    Args:
        query (str): The search keyword.
        search_type (str): The type of search - "title", "author", "abstract", "category", "id".
        max_results (int): The number of results to retrieve.
        sort_by (arxiv.SortCriterion): Sorting criterion (Relevance, Submission Date, Last Updated).

    Returns:
        list: A list of arXiv search results.
    """
    start_time = time.time()

    # Define search query based on type
    if search_type == "title":
        search = arxiv.Search(query=f'ti:"{query}"', max_results=max_results, sort_by=sort_by)
    elif search_type == "author":
        search = arxiv.Search(query=f'au:"{query}"', max_results=max_results, sort_by=sort_by)
    elif search_type == "category":
        search = arxiv.Search(query=f'cat:{query}', max_results=max_results, sort_by=sort_by)
    elif search_type == "abstract":
        search = arxiv.Search(query=f'abs:"{query}"', max_results=max_results, sort_by=sort_by)
    elif search_type == "id":
        search = arxiv.Search(id_list=[query])
    else:
        print("Invalid search type.")
        return []

    results = list(client.results(search))  # Convert iterator to list
    print_results(results)

    print(f"Search time ({search_type} - {sort_by.name}): {time.time() - start_time:.2f} seconds\n")
    return results


def print_results(results):
    """Prints the details of a list of arXiv results."""
    if not results:
        print("No results found.")
        return
    for result in results:
        print_result(result)


def print_result(result):
    """Prints a single arXiv research paper's details."""
    print(f"Title: {result.title}")
    print(f"Authors: {', '.join(a.name for a in result.authors)}")
    print(f"Published: {result.published}")
    print(f"Updated: {result.updated}")
    print(f"PDF: {result.pdf_url}\n")


search_term = "Deep Learning"

print("### SEARCH SORTED BY RELEVANCE ###")
arxiv_search(search_term, search_type="title", max_results=5, sort_by=arxiv.SortCriterion.Relevance)

print("\n### SEARCH SORTED BY SUBMISSION DATE ###")
arxiv_search(search_term, search_type="title", max_results=5, sort_by=arxiv.SortCriterion.SubmittedDate)

print("\n### SEARCH SORTED BY LAST UPDATED DATE ###")
arxiv_search(search_term, search_type="title", max_results=5, sort_by=arxiv.SortCriterion.LastUpdatedDate)
