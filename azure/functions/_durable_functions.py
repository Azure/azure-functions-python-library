from . import _abc


class OrchestrationContext(_abc.OrchestrationContext):
    """A durable function orchestration context.

    :param str body:
        The body of orchestration context.
    """

    def __init__(self,
                 body: str) -> None:
        self.__body = body

    @property
    def body(self):
        return self.__body

    def __repr__(self):
        return (
            f'<azure.OrchestrationContext '
            f'body={self.body}>'
        )
