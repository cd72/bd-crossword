# from . import index_page_parser
from bd_crossword.common import bd_request
from pathlib import Path
import logging
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


def convert_url_to_cache_file_name(title: str, cache_folder):
    title = title.replace(" ", "")
    cache_file_name = Path(f"{cache_folder}/{Path(title).name}.html")
    logger.debug(f"cache file name is {cache_file_name}")
    return cache_file_name


def get_html_from_disk_cache(url, cache_folder):
    cache_file_name = convert_url_to_cache_file_name(url, cache_folder)

    if cache_file_name.is_file():
        logger.debug(f"loading {cache_file_name} from disk cache")
        return cache_file_name.read_text(encoding="utf8")
    else:
        logger.debug("======= cache miss for %s,", cache_file_name)


def save_html_to_disk_cache(url, html, cache_folder):
    cache_file_name = convert_url_to_cache_file_name(url, cache_folder)

    logger.debug(f"saving html to cache file {cache_file_name}")
    cache_file_name.write_text(html, encoding="utf8")


def download_html_from(url):
    logger.info(f"..fetching page {url}")
    bd = bd_request.BDRequest(mean_interval=30)
    return bd.download_url(url)


def simplify_html_old(html):
    soup = BeautifulSoup(html, "html.parser")
    entry_content = soup.select_one(".entry-content")

    if not entry_content:
        Path("error.html").write_text(soup.prettify(), encoding="utf8")
        raise ValueError("Could not match entry, see error.html")

    return entry_content.prettify()


def simplify_html(html):
    #  30218 the Cryptic word is not included hence the non-capturing group (?:)
    re_basic_content_start = re.compile(
        r"""\>Daily\sTelegraph\s(?:Cryptic\s)?No.+""",
        re.VERBOSE + re.MULTILINE + re.DOTALL,
    )

    if match := re.search(re_basic_content_start, html):
        html = f"<h2{match.group()}"
    else:
        Path("error.html").write_text(html, encoding="utf8")
        raise ValueError("Could not match re_basic_content_start, see error.html")

    re_basic_content_end = re.compile(
        """.+class="spoiler".+?\n|<.+title="Answer.+?\n""", re.VERBOSE + re.MULTILINE + re.DOTALL
    )
    if match := re.search(re_basic_content_end, html):
        html = match.group()
    else:
        Path("error.html").write_text(html, encoding="utf8")
        raise ValueError("Could not match end.re_basic_content_end, see error.html")
    return html


def get_entry_page(
    title, url, cache_folder="bd_entry_page_cache", force_download=False
):
    Path(cache_folder).mkdir(parents=True, exist_ok=True)

    if not force_download:
        html = get_html_from_disk_cache(title, cache_folder)

    if not html:
        html = download_html_from(url)
        html = simplify_html(html)
        save_html_to_disk_cache(title, html, cache_folder)

    return html
