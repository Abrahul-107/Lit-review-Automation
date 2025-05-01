import requests
import urllib.parse

def search_openalex(title, max_results=5):
    base_url = "https://api.openalex.org/works"
    query = urllib.parse.quote(title)
    url = f"{base_url}?search={query}&per-page={max_results}"

    print(f"\n🔍 Searching for: {title}\n")

    response = requests.get(url)
    data = response.json()

    if "results" not in data or not data["results"]:
        print("❌ No results found.\n")
        return

    for idx, item in enumerate(data["results"], 1):
        title = item.get("title", "No title")
        authors = [author["author"]["display_name"] for author in item.get("authorships", [])]
        year = item.get("publication_year", "N/A")
        venue = item.get("host_venue", {}).get("display_name", "Unknown Journal")
        doi = item.get("doi")
        url = doi if doi else item.get("id")

        print(f"📄 Result {idx}:")
        print(f"Title   : {title}")
        print(f"Authors : {', '.join(authors) if authors else 'Unknown'}")
        print(f"Year    : {year}")
        print(f"Journal : {venue}")
        print(f"Link    : {url}\n")

# Example usage
if __name__ == "__main__":
    paper_title = input("Enter a paper title to search: ")
    search_openalex(paper_title)
