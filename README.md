# <img src="https://raw.githubusercontent.com/Azure/azure-functions-python-worker/dev/docs/Azure.Functions.svg" width = "40" alt="Functions Header Image - Lightning Logo"> Azure Functions Python Library

| Branch | CodeCov                                                                                                                                                            |
|--------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| master | [![codecov](https://codecov.io/gh/Azure/azure-functions-python-library/branch/master/graph/badge.svg)](https://codecov.io/gh/Azure/azure-functions-python-library) |
| dev    | [![codecov](https://codecov.io/gh/Azure/azure-functions-python-library/branch/dev/graph/badge.svg)](https://codecov.io/gh/Azure/azure-functions-python-library)    |

## Overview

Python support for Azure Functions is based on Python 3.6/3.7/3.8/3.9 and 3.10 (coming soon), serverless hosting on Linux and the Functions 2.0, 3.0
and 4.0 runtime.

Here is the current status of Python in Azure Functions:

_What are the supported Python versions?_

| Azure Functions Runtime | Python 3.6 | Python 3.7 | Python 3.8 | Python 3.9 |
|-------------------------|------------|------------|------------|------------|
| Azure Functions 3.0     | &#x2713;          | &#x2713;          | &#x2713;          | &#x2713;          |
| Azure Functions 4.0     | &#x2713;          | &#x2713;          | &#x2713;          | &#x2713;          |

_What's available?_
- Build, test, debug and publish using Azure Functions Core Tools (CLI) or Visual Studio Code
- Triggers / Bindings : HTTP, Blob, Queue, Timer, Cosmos DB, Event Grid, Event Hubs and Service Bus
- Create a Python Function on Linux using a custom docker image
- Triggers / Bindings : Custom binding support

#### Get Started

- [Create your first Python function](https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-first-function-python)
- [Developer guide](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Binding API reference](https://docs.microsoft.com/en-us/python/api/azure-functions/azure.functions?view=azure-python)
- [Develop using VS Code](https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-first-function-vs-code)
- [Create a Python Function on Linux using a custom docker image](https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-function-linux-custom-image)

#### Give Feedback

Issues and feature requests are tracked in a variety of places. To report this feedback, please file an issue to the relevant repository below:

| Item          | Description                                  | Link                                                                           |
|---------------|----------------------------------------------|--------------------------------------------------------------------------------|
| Python Worker | Programming Model, Triggers & Bindings       | [File an Issue](https://github.com/Azure/azure-functions-python-worker/issues) |
| Linux         | Base Docker Images                           | [File an Issue](https://github.com/Azure/azure-functions-docker/issues)        |
| Runtime       | Script Host & Language Extensibility         | [File an Issue](https://github.com/Azure/azure-functions-host/issues)          |
| VSCode        | VSCode Extension for Azure Functions         | [File an Issue](https://github.com/microsoft/vscode-azurefunctions/issues)     |
| Core Tools    | Command Line Interface for Local Development | [File an Issue](https://github.com/Azure/azure-functions-core-tools/issues)    |
| Portal        | User Interface or Experience Issue           | [File an Issue](https://github.com/azure/azure-functions-ux/issues)            |
| Templates     | Code Issues with Creation Template           | [File an Issue](https://github.com/Azure/azure-functions-templates/issues)     |

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
