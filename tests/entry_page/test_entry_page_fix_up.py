from bd_crossword.entry_page.entry_page_fix_up import fix_up_html
import re
import logging
logger = logging.getLogger(__name__)

# From DT 30163

# From DT 30151
    
def test_direction_header_in_same_paragraph_as_clue_02():
    html = """</p>
<p>Across<br />
1a <span style="text-decoration: underline;">Food</span> from disco somewhere in Kent (4,8)<br />
<span class="spoiler"><span class="hidden-content">CLUB SANDWICH"""
    logger.debug(fix_up_html(html))
    assert fix_up_html(html) == """</p>
<p>Across</p>
<p>1a <span style="text-decoration: underline;">Food</span> from disco somewhere in Kent (4,8)<br />
<span class="spoiler"><span class="hidden-content">CLUB SANDWICH"""


def test_mrk_clue_id():
    html="""<p><span id="c17d"></span><strong>17d</strong>   <span class="dls mk1"><span class="mk0">Cured pork</span></span> pate can't spread (8)<br/>"""
    assert fix_up_html(html) == """<p>17d   <span class="dls mk1"><span class="mk0">Cured pork</span></span> pate can't spread (8)<br/>"""

def test_spoilers():
    html = """<span class="km2" title="Answer"><span class="hc"> PANCETTA</span></span>"""
    assert fix_up_html(html) == """<span class="spoiler"> PANCETTA</span>"""