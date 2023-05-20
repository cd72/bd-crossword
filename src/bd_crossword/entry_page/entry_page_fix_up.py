import re
import logging

logger = logging.getLogger(__name__)

from bs4 import BeautifulSoup
from bs4 import NavigableString
from bs4 import Comment


def fix_up_spoilers(soup):
    def workaround_for_hint_being_included_in_spoiler_tag(soup):
        # e.g. DT-30075
        for tag in soup("spoiler"):
            logger.debug(tag.string)
            if tag.string is not None and ":" in tag.string:
                (solution, colon, hint) = tag.string.partition(":")
                logger.debug("solution is %s", solution)
                logger.debug("hint is %s", hint)
                tag.string = solution
                tag.insert_after(f":{hint}")
        return soup

    def unwrap_inner_spoiler_span(tag):
        if tag.span:
            tag.span.unwrap()
        tag.attrs = {}
        tag.name = "spoiler"

    for tag in soup.find_all("span", class_="spoiler"):
        unwrap_inner_spoiler_span(tag)

    # <span class="km2" title="Answer"><span class="hc">
    for tag in soup.find_all("span", class_="km2", title="Answer"):
        unwrap_inner_spoiler_span(tag)

    # <span class="mrkSpoiler" title="Answer"><span class="hidden-content">
    for tag in soup.find_all("span", class_="mrkSpoiler", title="Answer"):
        unwrap_inner_spoiler_span(tag)

    soup = workaround_for_hint_being_included_in_spoiler_tag(soup)
    return soup


def fix_up_underlines(soup):
    def unwrap_underline_tags(tag):
        if tag.span:
            tag.span.unwrap()
        tag.attrs = {}
        tag.name = "u"

    for tag in soup.find_all("span", style="text-decoration: underline;"):
        unwrap_underline_tags(tag)

    # <span class="dls mk1"><span class="mk0">
    for tag in soup.find_all("span", class_=["dls", "mk1"]):
        unwrap_underline_tags(tag)

    # <span class="mrkUnderS solid"><span class="mrkMoveS">
    for tag in soup.find_all("span", class_=["mrkUnderS", "solid"]):
        unwrap_underline_tags(tag)

    for tag in soup.find_all("span", class_=["mrkUnderD", "dot"]):
        unwrap_underline_tags(tag)

    for tag in soup.find_all("span", class_=["DLS", "MK1"]):
        unwrap_underline_tags(tag)

    # <span class="MRKUNDERS SOLID"><span class="MRKMOVES"
    for tag in soup.find_all("span", class_=["MRKUNDERS", "SOLID"]):
        unwrap_underline_tags(tag)
    return soup


def fix_up_styles(soup):
    for tag in soup("span"):
        if all(key in ["style", "id", "lang"] for key in tag.attrs.keys()):
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
    [tag.unwrap() for tag in soup("span", class_="km2")]
    [tag.unwrap() for tag in soup("span", class_="mrkSpoiler", title="hint")]
    [tag.unwrap() for tag in soup("span", class_="mrkSpoiler", title="Click here!")]
    [tag.unwrap() for tag in soup("span", class_="mrkSpoiler", title="Click here")]
    [
        tag.unwrap()
        for tag in soup(
            "span", class_="mrkSpoiler", title="Click here for an antelope word cloud"
        )
    ]
    [tag.unwrap() for tag in soup("span", class_="mrkSpoiler", title="Hint")]
    [tag.unwrap() for tag in soup("span", class_="mrkSpoiler", title="this example")]
    [tag.unwrap() for tag in soup("span", class_="mrkMoveDS")]
    [tag.unwrap() for tag in soup("span", class_="mrkMoveD")]
    return soup


def fix_up_brs(soup):
    for tag in soup.find_all("br"):
        tag.insert_after(f"\n")
        tag.unwrap()

    return soup


def capitalize_match(match):
    return match.group(1).capitalize()


def lowercase_match(match):
    return match.group(1).lower()


def fix_up_leading_and_trailing_spaces(result):
    re_fixup = re.compile(r"^ *(.+) *$", re.MULTILINE)
    (result, num_subs) = re.subn(re_fixup, r"\1", result)
    logger.debug("made %d subs", num_subs)
    return result

def fix_up_direction_headers(result):
    re_fixup = re.compile(r"^(Across|Down) +(?:Clues)?$", re.MULTILINE)
    (result, num_subs) = re.subn(re_fixup, r"\1", result)
    logger.debug("made %d subs", num_subs)

    re_fixup = re.compile(r"^ ?(Across|Down) ?$", re.MULTILINE + re.IGNORECASE)
    (result, num_subs) = re.subn(re_fixup, capitalize_match, result)
    logger.debug("made %d subs", num_subs)

    re_fixup = re.compile(r"^(Across|Down)\ hints.+$", re.MULTILINE + re.IGNORECASE)
    (result, num_subs) = re.subn(re_fixup, r"\1", result)
    logger.debug("'hints by' made %d subs", num_subs)

    re_fixup = re.compile(r"^Drown$", re.MULTILINE)
    (result, num_subs) = re.subn(re_fixup, "Down", result)
    logger.debug("made %d subs", num_subs)

    return result


def fix_up_daft_clue_ids(result):
    # e.g. 8ac. or 6d.
    re_fixup = re.compile(r"(\d{1,2}[a|d|A])c?\.? ", re.MULTILINE)
    (result, num_subs) = re.subn(re_fixup, r"\1 ", result)
    logger.debug("made %d subs", num_subs)
    return result


def fix_up_missing_close_bracket(result):
    re_fixup = re.compile(r"(^\d{1,2}[a|d] .+\([0-9,-]+$)", re.MULTILINE)
    (result, num_subs) = re.subn(re_fixup, r"\1)", result)
    logger.debug("made %d subs", num_subs)
    return result


def fix_up_close_bracket_on_next_line(result):
    re_fixup = re.compile(r"""
        ^(\d{1,2}[a|d]\s.+)\n
        (\([0-9,-]\))\n
    """, re.VERBOSE + re.MULTILINE)
    (result, num_subs) = re.subn(re_fixup, r"\1\2\n", result)
    logger.debug("made %d subs", num_subs)
    return result

def fix_up_hint_before_spoiler(result):
    re_fixup = re.compile(r"""
            ^(\d{1,2}[a|d].+\([0-9,-]+\)\n)
            (?<!\<spoiler)
            (.+\n
                (?:
                    (?<!\<spoiler).+
                )?\n?
            )
            (\<spoiler\>.+[:;])\n
            """,
        re.VERBOSE + re.MULTILINE,
    )
    (result, num_subs) = re.subn(re_fixup, r"\1\3\2",
        result,
    )
    logger.debug("made %d subs", num_subs)
    return result


def fix_up_uppercase_directions(result):
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
    (result, num_subs) = re.subn(
        re_fixup,
        lowercase_match,
        result,
    )
    logger.debug("made %d subs", num_subs)
    return result


def fix_up_dot_in_clue_length(result):
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
    (result, num_subs) = re.subn(
        re_fixup,
        r"\1\2,\3)",
        result,
    )
    logger.debug("made %d subs", num_subs)
    return result


def fix_up_missing_clue_length(result):
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
    (result, num_subs) = re.subn(
        re_fixup,
        r"\1 (0)\n\2",
        result,
    )
    logger.debug("made %d subs", num_subs)
    return result


def fix_up_spaces_before_clue_ids(result):
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
    (result, num_subs) = re.subn(
        re_fixup,
        r"\1\2 ",
        result,
    )
    logger.debug("made %d subs", num_subs)
    return result


def fix_up_html_03(html):
    soup = BeautifulSoup(html, "html.parser")
    soup = fix_up_spoilers(soup)

    soup = fix_up_underlines(soup)
    soup = fix_up_styles(soup)
    soup = decompose_unneeded_components(soup)

    soup = unwrap_unneeded_tags(soup)
    soup = fix_up_brs(soup)

    # with open("mid_soup_fixups.txt", "w") as file:
    #     file.write(str(soup))

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
    page_content = fix_up_leading_and_trailing_spaces(page_content)
    # with open("post_soup_fixups.txt", "w") as file:
    #     file.write(page_content)
    page_content = fix_up_direction_headers(page_content)
    # with open("page_content.txt", "w") as file:
    #     file.write(page_content)
    page_content = fix_up_daft_clue_ids(page_content)
    page_content = fix_up_missing_close_bracket(page_content)
    page_content = fix_up_close_bracket_on_next_line(page_content)
    page_content = fix_up_uppercase_directions(page_content)
    page_content = fix_up_dot_in_clue_length(page_content)
    page_content = fix_up_missing_clue_length(page_content)
    page_content = fix_up_spaces_before_clue_ids(page_content)
    page_content = fix_up_hint_before_spoiler(page_content)


    return page_content
