from . import _abc


class RetryContext(_abc.RetryContext):
    def __init__(self, strategy, max_retry_count, delay_interval,
                 minimum_interval, maximum_interval):
        self.__strategy = strategy
        self.__retry_count = 0
        self.__max_retry_count = max_retry_count
        self.__delay_interval = delay_interval
        self.__minimum_interval = minimum_interval
        self.__maximum_interval = maximum_interval
        self.__exception = None

    @property
    def retry_count(self):
        return self.__retry_count

    @property
    def exception(self):
        return self.__exception

    @property
    def strategy(self):
        return self.__strategy

    @property
    def max_retry_count(self):
        return self.__max_retry_count

    @property
    def delay_interval(self):
        return self.__delay_interval

    @property
    def minimum_interval(self):
        return self.__minimum_interval

    @property
    def maximum_interval(self):
        return self.__maximum_interval
