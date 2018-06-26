
import abc
import datetime
import typing


class ServiceBusMessage(abc.ABC):

    @abc.abstractmethod
    def get_body(self) -> bytes:
        """Return message body as bytes."""
        pass

    @property
    @abc.abstractmethod
    def content_type(self) -> typing.Optional[str]:
        """Message content type."""
        pass

    @property
    @abc.abstractmethod
    def correlation_id(self) -> typing.Optional[str]:
        """Message correlation identifier."""
        pass

    @property
    @abc.abstractmethod
    def expiration_time(self) -> typing.Optional[datetime.datetime]:
        """The date and time in UTC at which the message is set to expire."""
        pass

    @property
    @abc.abstractmethod
    def label(self) -> typing.Optional[str]:
        """Application specific label."""
        pass

    @property
    @abc.abstractmethod
    def message_id(self) -> str:
        """Identifier used to identify the message."""
        pass

    @property
    @abc.abstractmethod
    def partition_key(self) -> typing.Optional[str]:
        """Message partition key."""
        pass

    @property
    @abc.abstractmethod
    def reply_to(self) -> typing.Optional[str]:
        """The address of an entity to send replies to."""
        pass

    @property
    @abc.abstractmethod
    def reply_to_session_id(self) -> typing.Optional[str]:
        """A session identifier augmenting the reply_to address."""
        pass

    @property
    @abc.abstractmethod
    def scheduled_enqueue_time(self) -> typing.Optional[datetime.datetime]:
        """The date and time in UTC at which the message will be enqueued."""
        pass

    @property
    @abc.abstractmethod
    def session_id(self) -> typing.Optional[str]:
        """The session identifier for a session-aware entity."""
        pass

    @property
    @abc.abstractmethod
    def time_to_live(self) -> typing.Optional[datetime.timedelta]:
        """The TTL time interval."""
        pass

    @property
    @abc.abstractmethod
    def to(self) -> typing.Optional[str]:
        """The address of an entity the message is addressed."""
        pass

    @property
    @abc.abstractmethod
    def user_properties(self) -> typing.Dict[str, object]:
        """User-defined message metadata."""
        pass
