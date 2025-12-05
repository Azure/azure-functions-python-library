#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import logging

_logger = logging.getLogger('azure.functions.AsgiMiddleware')

df = None


def get_durable_package():
    """Determines which Durable SDK is being used.

    If the `azure-functions-durable` package is installed, we
    log a warning that this legacy package
    is deprecated.

    If both the legacy and current packages are installed,
    we log a warning and prefer the current package.

    If neither package is installed, we raise an exception.    
    """
    _logger.info("Attempting to import Durable Functions package.")
    using_legacy = False
    using_durable_task = False
    global df
    if df:
        _logger.info("Durable Functions package already loaded. DF: %s", df)
        return df

    try:
        import azure.durable_functions as durable_functions
        using_legacy = True
        _logger.warning("`azure-functions-durable` is deprecated. " \
        "Please migrate to the new `durabletask-azurefunctions` package. " \
        "See <AKA.MS LINK HERE> for more details.")
    except ImportError:
        _logger.info("`azure-functions-durable` package not found.")
        pass
    try:
        import durabletask.azurefunctions as durable_functions
        using_durable_task = True
    except ImportError:
        _logger.info("`durabletask-azurefunctions` package not found.")
        pass

    if using_durable_task and using_legacy:
        # Both packages are installed; prefer `durabletask-azurefunctions`.
        _logger.warning("Both `azure-functions-durable` and " \
        "`durabletask-azurefunctions` packages are installed. " \
        "The `durabletask-azurefunctions` package will be used.")
    
    if not using_durable_task and not using_legacy:
        error_message = \
                "Attempted to use a Durable Functions decorator, " \
                "but the `durabletask-azurefunctions` SDK package could not be " \
                "found. Please install `durabletask-azurefunctions` to use " \
                "Durable Functions."
        raise Exception(error_message)

    df = durable_functions

    return durable_functions
