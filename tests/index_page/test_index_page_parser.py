import logging
import pytest
from datetime import date
import pathlib
import dataclasses
import json
from bd_crossword.common import index_entry
import datetime


from bd_crossword.index_page import index_page_parser

logger = logging.getLogger(__name__)


########################################################
# Parsing only
########################################################
@pytest.mark.parametrize(
    "stars_input,expected_value",
    [
        ("*", 1),
        ("**", 2),
        ("***", 3),
        (" ***", 3),
        ("*** ", 3),
        ("****", 4),
        ("*****", 5),
        ("******", 6),
        ("*/**", 1.5),
        ("**/***", 2.5),
        ("***/****", 3.5),
        ("****/*****", 4.5),
        ("******", 6),
        ("**********", 10),
    ],
)
def test_stars_to_numbers(stars_input, expected_value):
    assert index_page_parser.convert_stars_to_number(stars_input) == expected_value


def test_stars_to_numbers_exception():
    stars_input = "***********"
    with pytest.raises(ValueError) as excinfo:
        index_page_parser.convert_stars_to_number(stars_input)
    assert "Invalid stars rating pattern found" in str(excinfo.value)
    assert stars_input in str(excinfo.value)


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        elif dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)

        return super(EnhancedJSONEncoder, self).default(obj)


def json_decode_object_hook(the_dict):
    for k, v in the_dict.items():
        if k in ["page_date"]:
            the_dict[k] = datetime.date.fromisoformat(v)
        elif k in ["last_updated"]:
            the_dict[k] = datetime.datetime.fromisoformat(v)
    return the_dict


def html_files():
    test_file_location = pathlib.Path(__file__).parent / "test_data_files"
    return sorted(list(test_file_location.rglob("*.html")))

def html_file_content():
    return [html_file.read_text() for html_file in html_files()]

def html_expected():
    for html_file in html_files():
        result_file = html_file.with_suffix(".index")

        try:
            expected_result_json = result_file.read_text()
            expected_result = json.loads(
                expected_result_json, object_hook=json_decode_object_hook
            )
        except json.decoder.JSONDecodeError as err:
            logger.warn(err)
            expected_result = {}
        except FileNotFoundError as err:
            logger.warn(err)
            result_file.write_text("{}")
            expected_result = {}

        yield expected_result

def html_name():
    return [html_file.stem.removeprefix("dump_")[:10] for html_file in html_files()]

def html_date_string():
    return [html_file.stem.removeprefix("dump_")[:10] for html_file in html_files()]


@pytest.mark.parametrize("html_content, expected_result, test_date_string", zip(html_file_content(), html_expected(), html_date_string()), ids=html_name())
class TestGetIndexEntriesForDate:
    def test_using_dump_file(self, html_content, expected_result, test_date_string):
        logger.debug("testing for name %s", test_date_string)

        [returned_index_entry] = index_page_parser.parse_index_page(
            html_content, date.fromisoformat(test_date_string)
        )

        index_entry_json = json.dumps(
            returned_index_entry,
            indent=4,
            sort_keys=True,
            cls=EnhancedJSONEncoder,
        )
        logger.debug("The json returned by the index page parser is")
        logger.debug(index_entry_json)

        logger.debug(
            "======================================================================"
        )
        logger.debug(f"{expected_result=}")
        expected_index_entry = index_entry.IndexEntry(**expected_result)

        assert returned_index_entry == expected_index_entry
