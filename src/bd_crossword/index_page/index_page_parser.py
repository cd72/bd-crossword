import logging
import re
from bs4 import BeautifulSoup
from bd_crossword.common import index_entry
from datetime import datetime


logger = logging.getLogger(__name__)


# Find the stars string for Difficulty
re_difficulty_stars = re.compile(
    r"""
    Difficulty          # The string Difficulty
    \s*                 # Optional space
    (
        \*[\*\/\ ]*              # one or more of the above set
    )
    """,
    re.VERBOSE + re.IGNORECASE,
)

re_enjoyment_stars = re.compile(
    r"""
    Enjoyment           # The string Enjoyment
    \s*                 # Optional space
    (
        \*[\*/\ ]*
    )
    """,
    re.VERBOSE + re.IGNORECASE,
)


def parse_string_for_difficulty(html_string):
    m = re_difficulty_stars.search(html_string)
    if not m:
        raise ValueError("NO DIFFICULTY FOUND")

    logger.debug(f"difficulty stars {repr(m.group(1))}")
    difficulty = convert_stars_to_number(m.group(1))
    logger.debug(f"difficulty: {difficulty}")
    return difficulty


def parse_string_for_enjoyment(html_string):
    m = re_enjoyment_stars.search(html_string)
    if not m:
        raise ValueError("NO ENJOYMENT FOUND")

    logger.debug(f"enjoyment stars {repr(m.group(1))}")
    enjoyment = convert_stars_to_number(m.group(1))
    logger.debug(f"enjoyment: {enjoyment}")
    return enjoyment


def convert_stars_to_number(stars):
    logger.debug(f"Stars input : {stars}")
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
    elif stars == "**********":  # http://bigdave44.com/2021/12/30/dt-29871/
        return 10
    else:
        raise (ValueError(f"Invalid stars rating pattern found : {stars}"))


def all_articles(soup):
    return soup.select("article")


def get_subtitles(entry_content):
    logger.debug(entry_content.prettify())
    subtitles = [
        subitem.lower().replace("\xa0", " ")
        for item in entry_content.select("h1, h2, strong, span, p")
        for subitem in item.text.splitlines()
    ]
    for subtitle in subtitles:
        logger.debug("subtitle_text : %s", subtitle)
    return subtitles


def all_index_entries(soup, index_date):
    logger.debug("in all_index_entries")

    for article in all_articles(soup):
        logger.debug("found article %s", article.text)
        entry_header = article.select_one(".entry-header")
        entry_content = article.select_one(".entry-content")
        entry_footer = article.select_one(".entry-footer")

        title_element = entry_header.select_one(".entry-title")
        title = " ".join(title_element.text.split())

        logger.debug("Title : %s", title)

        if not title.startswith("DT"):
            continue

        if "(Hints)" in title:
            continue

        if title == "DT 29606 (2021-02-17)":
            # workaround for the strange anomoly on http://bigdave44.com/2021/2/17
            continue

        subtitles = get_subtitles(entry_content)

        if any(subtitle.startswith("The Saturday") for subtitle in subtitles):
            continue

        if any(subtitle.startswith("A full review") for subtitle in subtitles):
            continue

        # Miffypops returns
        if (
            all("hints and tips" not in subtitle for subtitle in subtitles)
            and all("miffypops returns" not in subtitle for subtitle in subtitles)
            and all("hints tips" not in subtitle for subtitle in subtitles)
        ):

            logger.warning('No subtitle called "hints and tips" found')
            logger.debug(f"subtitles : {subtitles}")
            continue

        logger.debug(f"title : {title}")

        title_element = entry_header.select_one(".entry-title")
        url = title_element.select_one("a")["href"]
        logger.debug(f"url : {url}")
        author_element = entry_header.select_one(".author>a")
        hints_author = author_element.text
        logger.debug(f"hints_author : {hints_author}")

        if title in {"DT 29608", "DT 29759", "DT 29043", "DT 28840"}:
            # This one does not have difficulty or enjoyment set
            # bigdave44.com/2021/02/25/125809/
            # bigdave44.com/2021/8/20/
            difficulty = 3
            enjoyment = 3
        else:
            difficulty = parse_string_for_difficulty(entry_content.text)
            enjoyment = parse_string_for_enjoyment(entry_content.text)

        last_updated = datetime.fromisoformat(
            (entry_footer.select_one("time.updated")["datetime"])[:19]
        )
        logger.debug(f"Last Updated : {last_updated}")

        yield index_entry.IndexEntry(
            page_date=index_date,
            title=title,
            url=url,
            hints_author=hints_author,
            difficulty=difficulty,
            enjoyment=enjoyment,
            last_updated=last_updated,
        )


def parse_index_page(html, index_date):
    logger.info(f"making the soup with html of length {len(html)}")
    soup = BeautifulSoup(html, "html.parser")

    bd_pages = []
    logger.debug("starting loop")
    for entry in all_index_entries(soup, index_date):
        logger.debug("in loop")
        logger.info(entry)
        bd_pages.append(entry)
    return bd_pages
