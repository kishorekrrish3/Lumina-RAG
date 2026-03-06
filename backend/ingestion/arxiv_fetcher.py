import arxiv
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "data", "papers")

def fetch_papers(query, max_results=3):

    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    downloaded = []
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    for result in search.results():

        pdf_url = result.pdf_url
        title = re.sub(r'[^\w\s-]', '', result.title).strip().replace(" ", "_")

        filename = f"{title}.pdf"
        path = os.path.join(DOWNLOAD_FOLDER, filename)

        if not os.path.exists(path):
            print("Downloading:", title)
            try:
                result.download_pdf(dirpath=DOWNLOAD_FOLDER, filename=filename)
                downloaded.append(path)
            except Exception as e:
                print(f"Error downloading {title}: {e}")
        else:
            print(f"Already exists, skipping DB re-index: {title}")

    return downloaded