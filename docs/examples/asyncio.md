# Web Scraping with asyncio

Web scraping is the process of extracting useful data from websites, and it becomes especially challenging and time-consuming when dealing with hundreds or thousands of pages. Traditional synchronous scraping processes one page at a time, and is slow. asyncio allows us to take advantage of asynchronous I/O to scrape multiple pages concurrently, significantly speeding up the process but it is limited to a single core.

Modern computers often have multiple cores, but asyncio only takes advantage of a single core. However, with free-threaded Python, we can run multiple asyncio workers in threads to take advantage of all available cores.

This example demonstrates how to use free-threaded Python to run multiple asyncio workers in parallel, allowing us to scrape multiple pages concurrently across multiple cores.

It uses `aiohttp` for asynchronous HTTP requests and `bs4` for parsing HTML. The script scrapes Hacker News stories and their comments, demonstrating how to efficiently scrape a large number of pages using asyncio and free-threaded Python.

Install the required packages with:

```bash
pip install aiohttp beautifulsoup4
```

Code:

```python
# scraper.py

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter
from argparse import ArgumentParser

BASE_URL = "https://news.ycombinator.com/news?p={}"
ITEM_URL = "https://news.ycombinator.com/item?id={}"


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url, timeout=100) as response:
        return await response.text()


def parse_stories(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    stories = []

    for item in soup.select(".athing"):
        title_tag = item.select_one(".titleline > a")
        story_id = item.get("id")

        if title_tag and story_id:
            title = title_tag.text.strip()
            link = title_tag["href"].strip()
            stories.append({"id": story_id, "title": title, "link": link})

    return stories


def parse_comments(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    comments = []

    for row in soup.select("tr.comtr"):
        user_tag = row.select_one(".hnuser")
        comment_tag = row.select_one(".commtext")

        if user_tag and comment_tag:
            user = user_tag.text.strip()
            text = comment_tag.get_text(separator=" ", strip=True)
            comments.append({"user": user, "text": text})

    return comments


async def fetch_story_with_comments(
    session: aiohttp.ClientSession, story: dict
) -> dict:
    comment_html = await fetch(session, ITEM_URL.format(story["id"]))
    story["comments"] = parse_comments(comment_html)
    return story


async def worker(queue: Queue, all_stories: list) -> None:
    async with aiohttp.ClientSession() as session:
        while True:
            async with asyncio.TaskGroup() as tg:
                try:
                    page = queue.get(block=False)
                except Empty:
                    break
                html = await fetch(session, page)
                stories = parse_stories(html)
                if not stories:
                    break
                for story in stories:
                    tg.create_task(fetch_story_with_comments(session, story))
            all_stories.extend(stories)


def main(multithreaded: bool) -> None:
    queue = Queue()
    all_stories = []
    for page in range(1, 101):
        queue.put(BASE_URL.format(page))
    start_time = perf_counter()
    if multithreaded:
        print("Using multithreading for fetching stories...")
        workers: int = 8  # no of CPU cores to use
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for _ in range(workers):
                executor.submit(lambda: asyncio.run(worker(queue, all_stories)))
    else:
        print("Using single thread for fetching stories...")
        asyncio.run(worker(queue, all_stories))
    end_time = perf_counter()
    print(
        f"Scraping speed: {len(all_stories) / (end_time - start_time):.0f} stories/sec"
    )


if __name__ == "__main__":
    parser = ArgumentParser(description="Scrape Hacker News stories and comments.")
    parser.add_argument(
        "--multithreaded",
        action="store_true",
        default=False,
        help="Use multithreading for fetching stories.",
    )
    args = parser.parse_args()
    main(args.multithreaded)
```

To the program with single thread, run:

```bash
python scraper.py
```

To run the program with multiple threads, use the `--multithreaded` flag:

```bash
python scraper.py --multithreaded
```

To run the program with free-threaded Python:

```bash
python -X gil=0 scraper.py --multithreaded
```

Performance results on 12 core CPU:

| Configuration                      | Stories/sec |
| ---------------------------------- | ----------- |
| default build, single thread       | 12          |
| default build, multithreaded       | 35          |
| free-threaded build, multithreaded | 80          |

The default build performs better with multiple threads than better than single-threaded, because Python
releases the GIL during I/O operations, allowing other threads to run while waiting for network responses. This leads to some parallelism, but it is limited by the GIL.

The free-threaded build, however, allows for true parallelism across multiple cores, significantly increasing the scraping speed. This demonstrates how free-threaded Python can be used to efficiently scrape large amounts of data from the web by leveraging multiple cores.
