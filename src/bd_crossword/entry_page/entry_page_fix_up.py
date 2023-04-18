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
    
    (new_string, number_of_subs_made) = re.subn(re_search, re_replace, html)
    logger.debug("Made %d subs", number_of_subs_made)

    return re.sub(re_search, re_replace, html)

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
    return re.sub(re_mrk_clue_id, r"\1\2", html)

def fix_up_spoilers(html):
    html = html.replace(
        '<span class="km2" title="Answer"><span class="hc">',
        '<span class="spoiler"><span class="hidden-content">',
    )

    html = re.sub(
        r'\<span\ class="spoiler"\>\<span\ class="hidden-content"\>(.+?)\<\/span\>\<\/span\>',
        r'<span class="spoiler">\1</span>',
        html
    )

    return html

# def fix_up_direction_headers(html):
#     re_fixup_direction_headers = re.compile(
#         r"""
#             \<p\>
#             \<strong\>
#             (Across|Down)
#             .{0,10}?
#             \</strong\>
#             \s??                                 # Optional space
#             \</p\>
#             """,
#         re.VERBOSE + re.MULTILINE + re.DOTALL,
#     )
#     return re.sub(
#         re_fixup_direction_headers,
#         r"<p><strong>\1</strong></p>",
#         html,
#     )

def fix_up_html(html):
    html = fix_up_direction_header_with_no_paragraph(html)
    html = fix_up_mrk_clue_ids(html)
    html = fix_up_spoilers(html)
    return html
