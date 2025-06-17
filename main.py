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
        workers: int = 8 # no of CPU cores to use
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for _ in range(workers):
                executor.submit(lambda: asyncio.run(worker(queue, all_stories)))
    else:
        print("Using single thread for fetching stories...")
        asyncio.run(worker(queue, all_stories))
    end_time = perf_counter()
    print(f"Scraping speed: {len(all_stories) / (end_time - start_time):.0f} stories/sec")


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
