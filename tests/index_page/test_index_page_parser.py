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
    ],
)
def test_stars_to_numbers(stars_input, expected_value):
    assert index_page_parser.convert_stars_to_number(stars_input) == expected_value


def test_stars_to_numbers_exception():
    stars_input = "**********"
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


class TestGetIndexEntriesForDate:
    test_file_location = pathlib.Path(__file__).parent / "test_data_files"
    test_files = list(test_file_location.rglob("*.html"))
    assert len(test_files) > 1

    @pytest.fixture(params=test_files)
    def file_info(self, request):
        html_file = request.param
        result_file = html_file.with_suffix(".index")
        test_date_string = html_file.stem.removeprefix("dump_")[:10]

        logger.debug("using html file : %s", str(html_file.resolve()))
        logger.debug("using result file : %s", str(result_file.resolve()))
        html_content = html_file.read_text()

        expected_result_json = result_file.read_text()
        try:
            expected_result = json.loads(
                expected_result_json, object_hook=json_decode_object_hook
            )
        except json.decoder.JSONDecodeError as err:
            logger.warn(err)
            expected_result = {}

        logger.debug("expected result is :\n%s", expected_result)

        return {
            "html_content": html_content,
            "expected_result": expected_result,
            "test_date_string": test_date_string,
        }

    def test_using_dump_file(self, file_info):
        logger.debug("testing for date %s", file_info["test_date_string"])

        [returned_index_entry] = index_page_parser.parse_index_page(
            file_info["html_content"], date.fromisoformat(file_info["test_date_string"])
        )

        index_entry_json = json.dumps(
            returned_index_entry,
            indent=4,
            sort_keys=True,
            cls=EnhancedJSONEncoder,
        )
        print("The json is")
        print(index_entry_json)

        expected_result_dict = file_info["expected_result"]
        print("======================================================================")
        print(f"{expected_result_dict=}")
        expected_index_entry = index_entry.IndexEntry(**expected_result_dict)

        assert returned_index_entry == expected_index_entry
