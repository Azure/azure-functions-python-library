from typing import List, Tuple, Optional
from datetime import datetime


# Returns (parsed_datetime: datetime, matched_format: str, exc: Exception)
def try_parse_datetime_with_formats(
    datetime_str: str,
    datetime_formats: List[str]
) -> Tuple[Optional[datetime], Optional[str], Optional[Exception]]:
    for fmt in datetime_formats:
        try:
            dt = datetime.strptime(datetime_str, fmt)
            return (dt, fmt, None)
        except ValueError as ve:
            last_exception = ve

    return (None, None, last_exception)
