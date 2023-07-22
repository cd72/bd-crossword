from bd_crossword.entry_page.entry_page_fix_up import fix_up_html_03
import re
import logging
from bs4 import BeautifulSoup
from collections import Counter
import pytest
import pathlib
from typing import Set

logger = logging.getLogger(__name__)

# From DT 30163

# From DT 30151

# def test_direction_header_in_same_paragraph_as_clue_02():
#     html = """</p>
# <p>Across<br />
# 1a <span style="text-decoration: underline;">Food</span> from disco somewhere in Kent (4,8)<br />
# <span class="spoiler"><span class="hidden-content">CLUB SANDWICH"""
#     logger.debug(fix_up_html(html))
#     assert fix_up_html(html) == """</p>
# <p>Across</p>
# <p>1a <span style="text-decoration: underline;">Food</span> from disco somewhere in Kent (4,8)<br />
# <span class="spoiler"><span class="hidden-content">CLUB SANDWICH"""


# def test_mrk_clue_id():
#     html="""<p><span id="c17d"></span><strong>17d</strong>   <span class="dls mk1"><span class="mk0">Cured pork</span></span> pate can't spread (8)<br/>"""
#     assert fix_up_html(html) == """<p>17d   <span class="dls mk1"><span class="mk0">Cured pork</span></span> pate can't spread (8)<br/>"""

# def test_spoilers():
#     html = """<span class="km2" title="Answer"><span class="hc"> PANCETTA</span></span>"""
#     assert fix_up_html(html) == """<span class="spoiler"> PANCETTA</span>"""


glob_string = "DT301*.html"


def html_files():
    test_file_location = (
        pathlib.Path(__file__).parent.parent.parent / "bd_entry_page_cache"
    )
    return sorted(list(test_file_location.rglob(glob_string)))


def html_file_content():
    return [html_file.read_text() for html_file in html_files()]


def title_name():
    return [f.with_suffix("").name for f in html_files()]


@pytest.mark.parametrize(
    "html, id", zip(html_file_content(), title_name()), ids=title_name(), scope="class"
)
def test_no_tags(html, id):
    page_content = fix_up_html_03(html)

    content_soup = BeautifulSoup(page_content, "html.parser")
    tag_counter = Counter(
        [(tag.name, str(tag.attrs)) for tag in content_soup.find_all()]
    )
    logger.debug(tag_counter)

    tags_found = {tag[0] for tag in tag_counter}

    if id == "DT28445":  # This has answers visible
        assert tags_found == {"spoiler"}
    else:
        assert tags_found == {"u", "spoiler"}


all_disallowed_characters: Set[str] = set()
import string


@pytest.mark.parametrize(
    "html, id", zip(html_file_content(), title_name()), ids=title_name(), scope="class"
)
def test_no_special_characters(html, id):
    global all_disallowed_characters
    page_content = fix_up_html_03(html)

    allowed_characters = set(
        string.ascii_letters
        + string.digits
        + string.punctuation
        + "\n -°¡£©®¼⅓ÇÈÉÏÔ×àáâäçèéêëìíïñóôĀėřŵǝɐɹʍṚ"
    )
    page_characters = set(page_content)

    disallowed_characters = page_characters - allowed_characters

    logger.debug(disallowed_characters)
    all_disallowed_characters |= disallowed_characters
    assert disallowed_characters == set()


def test_all_special_characters():
    global all_disallowed_characters
    logger.debug
    assert not "".join(sorted(all_disallowed_characters))
