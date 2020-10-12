from typing import List


class CollectionBytes:
    def __init__(self, data: List[bytes]):
        self.bytes = data


class CollectionString:
    def __init__(self, data: List[str]):
        self.string = list(map(lambda x: x.encode('utf-8'), data))


class CollectionSint64:
    def __init__(self, data: List[int]):
        self.sint64 = data