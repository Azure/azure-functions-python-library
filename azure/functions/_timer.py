# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from . import _abc


class TimerRequest(_abc.TimerRequest):
    """A Timer Request object.

    :param bool past_due:
        An optional boolean specifying if the timer is past due.
    """

    def __init__(self, *, past_due: bool = False) -> None:
        self.__past_due = past_due

    @property
    def past_due(self) -> bool:
        """Whether the timer is past due."""
        return self.__past_due

    def to_dict(self):
        """Return a JSON-safe dictionary of timer request fields."""
        return {
            'past_due': self.past_due,
        }
