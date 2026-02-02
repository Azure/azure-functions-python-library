#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import logging

_logger = logging.getLogger('azure.functions.DurableFunctions')

df = None


def get_durable_package():
    """Determines which Durable SDK is being used.

    If the `azure-functions-durable` package is installed, we
    log a warning that this legacy package
    is deprecated.

    If both the legacy and current packages are installed,
    we log a warning and prefer the current package.

    If neither package is installed, we return None.
    """
    _logger.info("Attempting to import Durable Functions package.")
    using_legacy = False
    using_durable_task = False
    global df
    if df:
        _logger.info("Durable Functions package already loaded. DF: %s", df)
        return df

    try:
        import durabletask  # noqa
        using_durable_task = True
        _logger.info("`durabletask` package found.")
    except ImportError:
        _logger.info("`durabletask` package not found.")
        pass
    try:
        import azure.durable_functions  as durable_functions # noqa
        _logger.info("`azure.durable_functions` package found.")
    except ImportError:
        _logger.info("`azure.durable_functions` package not found.")
        pass

    if not using_durable_task and not using_legacy:
        return None

    df = durable_functions

    return durable_functions
