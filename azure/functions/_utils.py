from typing import List, Tuple
from datetime import datetime


# Returns (parsed_datetime, matched_format)
def try_parse_datetime_with_formats(
    datetime_str: str,
    datetime_formats: List[str]
) -> Tuple[bool, datetime, Exception]:
    for fmt in datetime_formats:
        try:
            dt = datetime.strptime(datetime_str, fmt)
            return (dt, fmt, None)
        except ValueError as ve:
            last_exception = ve

    return (None, None, last_exception)
