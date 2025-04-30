import requests
import os
import asyncio
import aiohttp
from datetime import datetime
from urllib.parse import urlparse

async def download_pdf(session, url, folder):
    filename = os.path.basename(urlparse(url).path) + ".pdf"
    filepath = os.path.join(folder, filename)

    try:
        async with session.get(url) as response:
            if response.status == 200:
                with open(filepath, "wb") as f:
                    content = await response.read()
                    f.write(content)
                print(f"✅ Downloaded {filename}")
            else:
                print(f"❌ Failed {filename}: Status {response.status}")
    except Exception as e:
        print(f"⚠️ Error downloading {filename}: {e}")


async def main(entries, folder_name):

    async with aiohttp.ClientSession() as session:
        tasks = [download_pdf(session, entry["URL"], folder_name) for entry in entries]
        await asyncio.gather(*tasks)

def download_research_paper(entries):
    # Check if entries is empty
    if not entries:
        print("No entries to download.")
        return

    # Create folder with current datetime
    folder_name = datetime.now().strftime("arxiv_downloads_%Y-%m-%d_%H%M%S")
    os.makedirs(folder_name, exist_ok=True)

    # Run the async main function
    asyncio.run(main(entries, folder_name))
    return folder_name

