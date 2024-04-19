from pydantic import ConstrainedStr


class ServiceName(ConstrainedStr):
    strip_whitespace = True
    min_length = 2
    max_length = 50
