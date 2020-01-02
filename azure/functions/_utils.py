from typing import List, Tuple
from datetime import datetime


# Returns (is_matched, parsed_datetime, matched_format)
def try_parse_datetime_with_formats(
    datetime_str: str,
    datetime_formats: List[str]
) -> Tuple[bool, datetime, str]:
    for fmt in datetime_formats:
        try:
            dt = datetime.strptime(datetime_str, fmt)
            return (True, dt, fmt)
        except ValueError:
            continue

    return (False, None, None)
