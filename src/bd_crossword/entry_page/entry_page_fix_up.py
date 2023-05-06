import re
import logging

logger = logging.getLogger(__name__)


def fix_up_direction_header_with_no_paragraph(html):
    re_search = re.compile(
        r"""
            (
            \<p\>
            \s*
            Across|Down
            \s*
            )
            \<br\s*\/\>
            \n
            (
            \d{1,2}[a|d]
            )
    """,
        re.VERBOSE + re.DOTALL + re.MULTILINE,
    )

    re_replace = r"""\1</p>\n<p>\2"""

    (result, number_of_subs_made) = re.subn(re_search, re_replace, html)
    logger.debug(
        "fix_up_direction_header_with_no_paragraph made %d subs", number_of_subs_made
    )

    return result


def fix_up_mrk_clue_ids(html):
    re_mrk_clue_id = re.compile(
        r"""
        <span\ id="c\d{1,2}[a|d]">
        </span>
        <strong>
        (\d{1,2})([a|d])
        </strong>
        """,
        re.VERBOSE,
    )
    (result, number_of_subs_made) = re.subn(re_mrk_clue_id, r"\1\2", html)
    logger.debug("fix_up_mrk_clue_ids made %d subs", number_of_subs_made)
    return result


def fix_up_spoilers_regex(html):
    html = html.replace(
        '<span class="km2" title="Answer"><span class="hc">',
        '<span class="spoiler"><span class="hidden-content">',
    )

    (result, number_of_subs_made) = re.subn(
        r'\<span\ class="spoiler"\>\<span\ class="hidden-content"\>(.+?)\<\/span\>\<\/span\>',
        r'<span class="spoiler">\1</span>',
        html,
    )
    logger.debug("fix_up_spoilers made %d subs", number_of_subs_made)

    return result


# <p><strong>Across</strong> </p
def fix_up_direction_headers_strong(html):
    re_fixup_direction_headers = re.compile(
        r"""
            \<p\>
            \<strong\>
            (Across|Down)
            .{0,10}?
            \</strong\>
            \s??                                 # Optional space
            \</p\>
            """,
        re.VERBOSE + re.MULTILINE + re.DOTALL,
    )
    (result, number_of_subs_made) = re.subn(
        re_fixup_direction_headers,
        r"<p>\1</p>",
        html,
    )
    logger.debug("made %d subs", number_of_subs_made)
    return result


def fix_up_direction_headers_b(html):
    re_fixup_direction_headers = re.compile(
        r"""
            \<p\>
            \<b\>
            (Across|Down)
            .{0,10}?
            \</b\>
            \s??                                 # Optional space
            \</p\>
            """,
        re.VERBOSE + re.MULTILINE + re.DOTALL,
    )
    (result, number_of_subs_made) = re.subn(
        re_fixup_direction_headers,
        r"<p>\1</p>",
        html,
    )
    logger.debug("made %d subs", number_of_subs_made)
    return result


def fix_up_mrk_clue_id_span(html):
    r = re.compile(
        r"""<span\ id="c\d{1,2}[a|d]"></span>""",
        re.VERBOSE + re.MULTILINE + re.DOTALL,
    )
    (result, number_of_subs) = re.subn(r, "", html)
    logger.debug("%s made %d subs", __name__, number_of_subs)

    result = result.replace('<span id="AcrossClues"></span>', "")
    result = result.replace('<span id="DownClues"></span>', "")

    return result


def fix_up_helvetica_span(html):
    r = re.compile(
        r"""\<span style=\"font-family: helvetica, arial, sans-serif;\"\>(.+?)\<\/span\>""",
        re.MULTILINE + re.DOTALL,
    )
    (result, number_of_subs) = re.subn(r, r"\1", html)
    logger.debug("made %d subs", number_of_subs)

    return result


def fix_up_color_span(html):
    r = re.compile(
        r"""\<span\sstyle=\"color:\s\#0000ff;\"\>(.+?)\<\/span\>""",
        re.VERBOSE + re.MULTILINE + re.DOTALL,
    )

    (result, number_of_subs) = re.subn(r, r"\1", html)
    logger.debug("made %d subs", number_of_subs)

    return result


def fix_up_html(html):
    html = fix_up_direction_headers_strong(html)
    html = fix_up_direction_headers_b(html)
    html = fix_up_mrk_clue_ids(html)
    html = fix_up_spoilers_regex(html)
    html = fix_up_mrk_clue_id_span(html)
    html = fix_up_color_span(html)
    html = fix_up_helvetica_span(html)
    html = fix_up_direction_header_with_no_paragraph(html)

    return html


from bs4 import BeautifulSoup
from bs4 import NavigableString
from bs4 import Comment

def unwrap_inner_spoiler_span(tag):
    if tag.span:
        tag.span.unwrap()
    tag.attrs = {}
    tag.name = "spoiler"


def fix_up_spoilers(soup):
    for tag in soup.find_all("span", class_="spoiler"):
        unwrap_inner_spoiler_span(tag)
    
    # <span class="km2" title="Answer"><span class="hc">
    for tag in soup.find_all("span", class_="km2", title="Answer"):
        unwrap_inner_spoiler_span(tag)

    # <span class="mrkSpoiler" title="Answer"><span class="hidden-content">
    for tag in soup.find_all("span", class_="mrkSpoiler", title="Answer"):
        unwrap_inner_spoiler_span(tag)

    for tag in soup("spoiler"):
        logger.debug(tag.string)
        if tag.string is not None and ":" in tag.string:
            (solution, colon, hint) = tag.string.partition(":")
            logger.debug("solution is %s", solution)
            logger.debug("solution type is %s", type(solution))
            logger.debug("hint is %s", hint)
            logger.debug("hint type is %s", type(hint))
            tag.string = solution
            tag.insert_after(f":{hint}")
            # assert 1 == 0

    return soup

def fix_up_underlines(soup):
    for tag in soup.find_all(
        "span", style="text-decoration: underline;"
    ):  # , class_="spoiler"):
        tag.attrs = {}
        tag.name = "u"

    # <span class="dls mk1"><span class="mk0">
    for tag in soup.find_all("span", class_=["dls", "mk1"]):
        if tag.span:
            tag.span.unwrap()
        tag.attrs = {}
        tag.name = "u"

    # <span class="mrkUnderS solid"><span class="mrkMoveS">
    for tag in soup.find_all("span", class_=["mrkUnderS", "solid"]):
        if tag.span:
            tag.span.unwrap()
        tag.attrs = {}
        tag.name = "u"

    for tag in soup.find_all("span", class_=["mrkUnderD", "dot"]):
        if tag.span:
            tag.span.unwrap()
        tag.attrs = {}
        tag.name = "u"


    for tag in soup.find_all("span", class_=["DLS", "MK1"]):
        if tag.span:
            tag.span.unwrap()
        tag.attrs = {}
        tag.name = "u"

    # <span class="MRKUNDERS SOLID"><span class="MRKMOVES"
    for tag in soup.find_all("span", class_=["MRKUNDERS", "SOLID"]):
        if tag.span:
            tag.span.unwrap()
        tag.attrs = {}
        tag.name = "u"
    return soup

def  fix_up_styles(soup):
    for tag in soup("span"):
        # logger.debug(tag.attrs.keys())
        if all(key in ["style", "id", "lang"] for key in tag.attrs.keys()):
            logger.debug("Removing style %s from tag %s", tag.attrs, tag.name)
            tag.unwrap()
    return soup

def decompose_unneeded_components(soup):
    for element in soup(string=lambda text: isinstance(text, Comment)):
        element.extract()

    [tag.decompose() for tag in soup("noscript")]
    [tag.decompose() for tag in soup("script")]
    [tag.decompose() for tag in soup("img")]
    [tag.decompose() for tag in soup("video")]
    [tag.decompose() for tag in soup("del")]
    [tag.decompose() for tag in soup("iframe")]
    [tag.decompose() for tag in soup("span", class_="embed-youtube")]
    [tag.decompose() for tag in soup("span", class_="arve-inner")]
    [tag.decompose() for tag in soup("span", class_="arve-embed")]
    [tag.decompose() for tag in soup("span", class_="arve-ar")]
    [tag.decompose() for tag in soup("span", class_="arve-error")]
    [tag.decompose() for tag in soup("a")]
    [tag.decompose() for tag in soup("hr")]
    [tag.decompose() for tag in soup("ul")]
    [tag.decompose() for tag in soup("li")]
    [tag.decompose() for tag in soup("ol")]
    [tag.decompose() for tag in soup("form")]
    [tag.decompose() for tag in soup("table")]
    [tag.decompose() for tag in soup("blockquote")]
    [tag.decompose() for tag in soup("dl")]
    [tag.decompose() for tag in soup("footer")]
    [tag.decompose() for tag in soup("nav")]
    [tag.decompose() for tag in soup("figure")]
    [tag.decompose() for tag in soup("fill")]
    [tag.decompose() for tag in soup("style", type="text/css")]
    return soup
      

def unwrap_unneeded_tags(soup):
    [tag.unwrap() for tag in soup("strong")]
    [tag.unwrap() for tag in soup("em")]
    [tag.unwrap() for tag in soup("div")]
    [tag.unwrap() for tag in soup("i")]
    [tag.unwrap() for tag in soup("b")]
    [tag.unwrap() for tag in soup("span", class_="hidden-content")]
    [tag.unwrap() for tag in soup("p")]
    [tag.unwrap() for tag in soup("h2")]
    [tag.unwrap() for tag in soup("sup")]
    [tag.unwrap() for tag in soup("span", class_="_Tgc")]
    [tag.unwrap() for tag in soup("span", class_="mrkHintSpacing")]
    [tag.unwrap() for tag in soup("span", class_="mk2")]
    [tag.unwrap() for tag in soup("span", class_="hc")]
    [tag.unwrap() for tag in soup("span", class_="s1")]
    [tag.unwrap() for tag in soup("span", class_="s2")]
    [tag.unwrap() for tag in soup("span", class_="Xspoiler")]
    [tag.unwrap() for tag in soup("span", class_="mrkSpoiler", title="Pun")]
    [tag.unwrap() for tag in soup("span", class_=["tod", "mk3"])]
    [tag.unwrap() for tag in soup("span", class_=["dash", "pbSD"])]
    [tag.unwrap() for tag in soup("span", class_="km4")]
    [tag.unwrap() for tag in soup("span", class_="hsa")]
    # [tag.unwrap() for tag in soup("span", class_="km2", title="hinty example")]
    # [tag.unwrap() for tag in soup("span", class_="km2", title="Hint")]
    # [tag.unwrap() for tag in soup("span", class_="km2", title="explanation")]
    # [tag.unwrap() for tag in soup("span", class_="km2", title="word")]
    # [tag.unwrap() for tag in soup("span", class_="km2", title="synonym")]
    # [tag.unwrap() for tag in soup("span", class_="km2", title="Click here!")]
    # [tag.unwrap() for tag in soup("span", class_="km2", title="Pun")]
    # [tag.unwrap() for tag in soup("span", class_="km2", title="Warning: contains answer")]
    # [tag.unwrap() for tag in soup("span", class_="km2", title="spoiler")]
    # [tag.unwrap() for tag in soup("span", class_="km2", title="hint")]
    [tag.unwrap() for tag in soup("span", class_="km2")]

    [tag.unwrap() for tag in soup("span", class_="mrkSpoiler", title="hint")]
    [tag.unwrap() for tag in soup("span", class_="mrkSpoiler", title="Click here!")]
    [tag.unwrap() for tag in soup("span", class_="mrkSpoiler", title="Click here")]
    [tag.unwrap() for tag in soup("span", class_="mrkSpoiler", title="Click here for an antelope word cloud")]
    [tag.unwrap() for tag in soup("span", class_="mrkSpoiler", title="Hint")]
    [tag.unwrap() for tag in soup("span", class_="mrkSpoiler", title="this example")]
    [tag.unwrap() for tag in soup("span", class_="mrkMoveDS")]
    [tag.unwrap() for tag in soup("span", class_="mrkMoveD")]
    return soup

def fix_up_brs(soup):
    for tag in soup.find_all("br"):
        tag.replace_with(NavigableString("\n"))
    return soup

def capitalize_match(match):
    return match.group(1).capitalize()

def lowercase_match(match):
    return match.group(1).lower()

def fix_up_direction_headers(html):
    re_fixup_direction_headers = re.compile(
        r"""
            ^
            (Across|Down)
            \ +
            (?:Clues)?
            $
        """,
        re.VERBOSE + re.MULTILINE,
    )
    (result, number_of_subs_made) = re.subn(
        re_fixup_direction_headers,
        r"\1",
        html,
    )
    logger.debug("made %d subs", number_of_subs_made)

    re_fixup_direction_headers = re.compile(
        r"""
            ^
            \s?
            (Across|Down)
            \s?
            $
        """,
        re.VERBOSE + re.MULTILINE + re.IGNORECASE,
    )
    (result, number_of_subs_made) = re.subn(
        re_fixup_direction_headers,
        capitalize_match,
        result,
    )
    logger.debug("made %d subs", number_of_subs_made)
    return result

def fix_up_daft_clue_ids(html):
    # e.g. 8ac. or 6d.
    re_fixup = re.compile(
        r"""
            (
                \d{1,2}
                [a|d|A]
            )
            c?
            \.?
            \s
            """,
        re.VERBOSE + re.MULTILINE,
    )
    (result, number_of_subs_made) = re.subn(
        re_fixup,
        r"\1 ",
        html,
    )
    logger.debug("made %d subs", number_of_subs_made)
    return result

def fix_up_missing_close_bracket(html):
    re_fixup = re.compile(
        r"""
            (
                ^
                \d{1,2}
                [a|d]
                \s
                .+
                \([0-9,-]+
                $
            )
            """,
        re.VERBOSE + re.MULTILINE,
    )
    (result, number_of_subs_made) = re.subn(
        re_fixup,
        r"\1)",
        html,
    )
    logger.debug("made %d subs", number_of_subs_made)
    return result


def fix_up_close_bracket_on_next_line(html):
    re_fixup = re.compile(
        r"""
            ^
            (
                \d{1,2}
                [a|d]
                \s
                .+
            )
            \n
            (
                \([0-9,-]\)
            )
            \n
            """,
        re.VERBOSE + re.MULTILINE,
    )
    (result, number_of_subs_made) = re.subn(
        re_fixup,
        r"\1\2\n",
        html,
    )
    logger.debug("made %d subs", number_of_subs_made)
    return result

def fix_up_uppercase_directions(html):
    # e.g. 8A
    re_fixup = re.compile(
        r"""
            ^
            (
                \d{1,2}
                [A|D]
                \s
            )
            """,
        re.VERBOSE + re.MULTILINE,
    )
    (result, number_of_subs_made) = re.subn(
        re_fixup,
        lowercase_match,
        html,
    )
    logger.debug("made %d subs", number_of_subs_made)
    return result

def fix_up_dot_in_clue_length(html):
    # e.g. (6.6)
    re_fixup = re.compile(
        r"""
            ^
            (
                \d{1,2}
                [a|d]
                \s
                .+
                \(
            )
            (\d)
            \.
            (\d)
            \)$
            """,
        re.VERBOSE + re.MULTILINE,
    )
    (result, number_of_subs_made) = re.subn(
        re_fixup,
        r"\1\2,\3)",
        html,
    )
    logger.debug("made %d subs", number_of_subs_made)
    return result

def fix_up_missing_clue_length(html):
    re_fixup = re.compile(
        r"""
            ^
            (
                \d{1,2}
                [a|d]
                \s
                .+
                (?<!
                        [0-9]\)
                )
            )
           \n
           (\<spoiler\>)
            """,
        re.VERBOSE + re.MULTILINE,
    )
    (result, number_of_subs_made) = re.subn(
        re_fixup,
        r"\1 (0)\n\2",
        html,
    )
    logger.debug("made %d subs", number_of_subs_made)
    return result

def fix_up_spaces_before_clue_ids(html):
    re_fixup = re.compile(
        r"""
            ^
            \ *
            (
                \d{1,2}
            )
            \ *
            (
                [a|d]
            )
            \ +
        """,
        re.VERBOSE + re.MULTILINE,
    )
    (result, number_of_subs_made) = re.subn(
        re_fixup,
        r"\1\2 ",
        html,
    )
    logger.debug("made %d subs", number_of_subs_made)
    return result

def fix_up_html_03(html):
    soup = BeautifulSoup(html, "html.parser")
    soup = fix_up_spoilers(soup)
    soup = fix_up_underlines(soup)
    soup = fix_up_styles(soup)
    soup = decompose_unneeded_components(soup)
    soup = unwrap_unneeded_tags(soup)
    soup = fix_up_brs(soup)

    soup.smooth()
    soup_strings = list(soup.strings)
    for s in soup_strings:
        (new, replacements) = re.subn(r"\n{2,}", "\n", s)
        if replacements > 0:
            # logger.debug("=== REPLACING ===")
            s.replace_with(new)

    page_content = str(soup)

    page_content = page_content.replace("\xa0", " ")
    page_content = page_content.replace("’", "'")
    page_content = page_content.replace("–", "-")
    page_content = page_content.replace("—", "-")
    page_content = page_content.replace("‘", "'")
    page_content = page_content.replace("“", '"')
    page_content = page_content.replace("”", '"')
    page_content = page_content.replace("…", "...")
    page_content = page_content.replace("\t", " ")
    page_content = page_content.replace("😊", "")
    page_content = page_content.replace("🇧🇬", "")
    page_content = page_content.replace("\x0b", "")
    page_content = page_content.replace("‑", "-")
    page_content = page_content.replace("″", '"')
    page_content = page_content.replace("′", "'")
    page_content = page_content.replace("•", "-")
    page_content = page_content.replace("ﬁ", "fi")
    page_content = page_content.replace("\u200b", "")
    page_content = page_content.replace("\u2028", "")
    page_content = page_content.replace("🇬", "")
    page_content = page_content.replace("🇧", "")
    page_content = page_content.replace("−", "-")
    page_content = page_content.replace("´", "'")
    page_content = page_content.replace("‟", '"')
    page_content = fix_up_direction_headers(page_content)
    page_content = fix_up_daft_clue_ids(page_content)
    page_content = fix_up_missing_close_bracket(page_content)
    page_content = fix_up_close_bracket_on_next_line(page_content)
    page_content = fix_up_uppercase_directions(page_content)
    page_content = fix_up_dot_in_clue_length(page_content)
    page_content = fix_up_missing_clue_length(page_content)
    page_content = fix_up_spaces_before_clue_ids(page_content)
    
    with open("page_content.txt", "w") as file:
        file.write(page_content)

    return page_content
