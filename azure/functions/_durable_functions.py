from typing import Union
from . import _abc


class OrchestrationContext(_abc.OrchestrationContext):
    """A durable function orchestration context.

    :param str body:
        The body of orchestration context json.
    """

    def __init__(self,
                 body: Union[str, bytes]) -> None:
        if isinstance(body, str):
            self.__body = body
        if isinstance(body, bytes):
            self.__body = body.decode('utf-8')

    @property
    def body(self) -> str:
        return self.__body

    def __repr__(self):
        return (
            f'<azure.OrchestrationContext '
            f'body={self.body}>'
        )

    def __str__(self):
        return self.__body
