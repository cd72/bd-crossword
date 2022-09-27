import logging
import requests
import re
from datetime import timedelta
from bs4 import BeautifulSoup
from dataclasses import dataclass, field


logger = logging.getLogger(__name__)

headers = {
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

url_template = "http://bigdave44.com/{year}/{month}/{day}"


# Find the stars string for Difficulty
re_difficulty_stars = re.compile(
    r"""
    Difficulty          # The string Difficulty
    \s?                 # Optional space
    (
        [\*\/\ ]+              # one or more of the above set
    )
    """,
    re.VERBOSE,
)

re_enjoyment_stars = re.compile(
    r"""
    Enjoyment           # The string Enjoyment
    \s?                 # Optional space
    (
        [\*/\ ]+
    )
    """,
    re.VERBOSE,
)


@dataclass
class IndexEntry:
    title: str
    url: str
    hints_author: str
    difficulty: str
    enjoyment: str
    last_updated: str


def get_puzzle_title(soup):
    puzzle_title = soup.select_one("h1.entry-title").text
    logger.info(f"Puzzle title is {puzzle_title}")
    return puzzle_title


def get_puzzle_author(soup):
    puzzle_author = soup.select_one("span.author").text
    logger.info(f"Puzzle author is {puzzle_author}")
    return puzzle_author


def parse_string_for_difficulty(html_string):
    m = re_difficulty_stars.search(html_string)
    if not m:
        raise Exception("NO DIFFICULTY FOUND")

    logger.debug(f"difficulty stars {repr(m.group(1))}")
    difficulty = convert_stars_to_number(m.group(1))
    logger.debug(f"difficulty: {difficulty}")
    return difficulty


def parse_string_for_enjoyment(html_string):
    m = re_enjoyment_stars.search(html_string)
    if not m:
        raise Exception("NO ENJOYMENT FOUND")

    logger.debug(f"enjoyment stars {repr(m.group(1))}")
    enjoyment = convert_stars_to_number(m.group(1))
    logger.debug(f"enjoyment: {enjoyment}")
    return enjoyment


def convert_stars_to_number(stars):
    stars = stars.replace(" ", "")
    if stars == "*":
        return 1
    elif stars == "**":
        return 2
    elif stars == "***":
        return 3
    elif stars == "****":
        return 4
    elif stars == "*****":
        return 5
    elif stars == "******":
        return 6
    elif stars == "*/**":
        return 1.5
    elif stars == "**/***":
        return 2.5
    elif stars == "***/****":
        return 3.5
    elif stars == "****/*****":
        return 4.5
    else:
        return 999


def dates_in_range(start_date, days):
    one_day = timedelta(days=1)
    return (start_date - (day_count * one_day) for day_count in range(days))


def download_index_for_date(index_date):
    url = url_template.format(
        year=index_date.year, month=index_date.month, day=index_date.day
    )
    logger.info(f"..fetching page {url}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def all_index_entries(soup):
    articles = soup.select("article")
    for article in articles:
        print("processing article")
        entry_header = article.select_one(".entry-header")
        entry_content = article.select_one(".entry-content")
        entry_footer = article.select_one(".entry-footer")

        title_element = entry_header.select_one(".entry-title")
        title = title_element.text

        print(f"{title=}")

        if not title.startswith("DT"):
            continue

        if "(Hints)" in title:
            continue

        # for subtitle in list(entry_content.select('h2')):
        #    if subtitle.text.startswith('A full review'):
        #        continue
        #    if subtitle.text.startswith('The Saturday Crossword Club'):
        #        continue

        if any(
            subtitle.text.startswith("The Saturday")
            for subtitle in entry_content.select("h2")
        ):
            continue
        print("ok1")

        if not any(
            subtitle.text.startswith("Hints and tips")
            for subtitle in entry_content.select("h2")
        ):
            print("invalid subtitle")
            for subtitle in entry_content.select("h2"):
                print("===" + str(subtitle))
                print(subtitle.text.startswith("Hints and tips"))
            continue

        logger.debug(f"title : {title}")
        url = title_element.select_one("a")["href"]
        logger.debug(f"url : {url}")

        author_element = entry_header.select_one(".author>a")
        hints_author = author_element.text
        logger.debug(f"hints_author : {hints_author}")
        print(f"hints_author : {hints_author}")

        if title == "DT 29608":
            # This one does not have difficulty or enjoyment set
            # bigdave44.com/2021/02/25/125809/
            difficulty = 3
            enjoyment = 3
        else:
            difficulty = parse_string_for_difficulty(entry_content.text)
            logger.debug(f"Difficulty : {difficulty}")

            enjoyment = parse_string_for_enjoyment(entry_content.text)
            logger.debug(f"Enjoyment : {enjoyment}")

        last_updated = entry_footer.select_one("time.updated")["datetime"]
        logger.debug(f"Last Updated : {last_updated}")

        item = IndexEntry(
            title=title,
            url=url,
            hints_author=hints_author,
            difficulty=difficulty,
            enjoyment=enjoyment,
            last_updated=last_updated,
        )
        print(item)
        yield (item)


def parse_index_page(html):
    logger.info("making the soup")
    soup = BeautifulSoup(html, "html.parser")
    # sp = soup.prettify()

    bd_pages = []
    for entry in all_index_entries(soup):
        logger.info(entry)
        print("entry is " + repr(entry))
        bd_pages.append(entry)

    return bd_pages


def get_index_entries_for_date(index_date):
    logger.debug(f"{index_date=}")
    html_text = download_index_for_date(index_date)
    logger.debug("html length : %d", len(html_text))
    logger.debug("html : %s", html_text[:100])
    entries_for_date = parse_index_page(html_text)
    logger.info(entries_for_date)
    print(entries_for_date)


def download_date_range(start_date, days):
    logger.debug(f"{start_date=}")
    logger.debug(f"{days=}")

    for index_date in dates_in_range(start_date, days):
        entries_for_date = get_index_entries_for_date(index_date)
