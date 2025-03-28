'''
@author:Rahul parida
date:11/02/2025 23.34'''

import arxiv
import time

#Initialize arXiv client
client = arxiv.Client()

def search_by_title(title: str, max_results: int = 15):
    """
    Search for research papers on arXiv by title.

    Args:
        title (str): The title or keywords to search for in the paper titles.
        max_results (int, optional): The maximum number of results to retrieve. Default is 5.

    Returns:
        None: Prints the paper details including title, authors, publication date, and PDF link.
    """
    start_time = time.time()
    search = arxiv.Search(
        query=f'ti:"{title}"', 
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    final_result = []
    for result in client.results(search):
        print_result(result)
        final_result.append(result)
    print(f"Total time taken: {time.time() - start_time:.2f} seconds\n")
    return final_result

def search_by_author(author: str, max_results: int = 5):
    """
    Search for research papers on arXiv by author name.

    Args:
        author (str): The name of the author to search for.
        max_results (int, optional): The maximum number of results to retrieve. Default is 5.

    Returns:
        None: Prints the paper details including title, authors, publication date, and PDF link.
    """
    start_time = time.time()
    search = arxiv.Search(
        query=f'au:"{author}"', 
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    for result in client.results(search):
        print_result(result)
    print(f"Total time taken: {time.time() - start_time:.2f} seconds\n")



def search_by_category(category: str, max_results: int = 5):
    """
    Search for research papers on arXiv by category.

    Args:
        category (str): The category code to search in (e.g., "cs.LG" for machine learning).
        max_results (int, optional): The maximum number of results to retrieve. Default is 5.

    Returns:
        None: Prints the paper details including title, authors, publication date, and PDF link.
    """
    start_time = time.time()
    search = arxiv.Search(
        query=f'cat:{category}', 
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    for result in client.results(search):
        print_result(result)
    print(f"Total time taken: {time.time() - start_time:.2f} seconds\n")



def search_by_abstract(keyword: str, max_results: int = 5):
    """
    Search for research papers on arXiv by keyword in the abstract.

    Args:
        keyword (str): The keyword to search for in the paper abstracts.
        max_results (int, optional): The maximum number of results to retrieve. Default is 5.

    Returns:
        None: Prints the paper details including title, authors, publication date, and PDF link.
    """
    start_time = time.time()
    search = arxiv.Search(
        query=f'abs:"{keyword}"', 
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    for result in client.results(search):
        print_result(result)
    print(f"Total time taken: {time.time() - start_time:.2f} seconds\n")



def search_by_id(paper_id: str):
    """
    Retrieve a specific research paper on arXiv by its unique paper ID.

    Args:
        paper_id (str): The unique identifier of the paper (e.g., "2401.12345").

    Returns:
        None: Prints the paper details including title, authors, publication date, and PDF link.
    """
    start_time = time.time()
    search = arxiv.Search(id_list=[paper_id])
    for result in client.results(search):
        print_result(result)
    print(f"Total time taken: {time.time() - start_time:.2f} seconds\n")



def print_result(result):
    """
    Print the details of a given arXiv research paper.

    Args:
        result (arxiv.Result): The result object containing paper details.

    Returns:
        None: Prints the title, authors, publication date, and PDF link of the paper.
    """
  
