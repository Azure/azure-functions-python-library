# <img src="https://raw.githubusercontent.com/Azure/azure-functions-python-worker/dev/docs/Azure.Functions.svg" width = "40" alt="Functions Header Image - Lightning Logo"> Azure Functions Python Library

| Branch | CodeCov                                                                                                                                                            |
|--------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| master | [![codecov](https://codecov.io/gh/Azure/azure-functions-python-library/branch/master/graph/badge.svg)](https://codecov.io/gh/Azure/azure-functions-python-library) |
| dev    | [![codecov](https://codecov.io/gh/Azure/azure-functions-python-library/branch/dev/graph/badge.svg)](https://codecov.io/gh/Azure/azure-functions-python-library)    |

## Overview

Python support for Azure Functions is based on Python 3.10, 3.11, 3.12, and 3.13 serverless hosting on Linux, and the Functions 2.x ([EOL](https://learn.microsoft.com/azure/azure-functions/functions-versions?#retired-versions)), 3.x ([EOL](https://learn.microsoft.com/azure/azure-functions/functions-versions?#retired-versions)) and 4.0 runtime.

Here is the current status of Python in Azure Functions:

_What are the supported Python versions?_

| Azure Functions Runtime          | Python 3.10 | Python 3.11 | Python 3.12 | Python 3.13 |
|----------------------------------|------------|------------|-------------|-------------|
| Azure Functions 4.0              | ✔          | ✔          | ✔           | ✔           |                                                                              | &#x2713;    | &#x2713;    | &#x2713;    |

_What's available?_
- Build, test, debug and publish using Azure Functions Core Tools (CLI) or Visual Studio Code
- Triggers / Bindings : Blob, Cosmos DB, Event Grid, Event Hub, HTTP, Kafka, MySQL, Queue, ServiceBus, SQL, Timer, and Warmup
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

## Durable Functions JSON serialization

`azure.functions._durable_functions.df_dumps` emits ordinary Unicode literally
in both loose and strict typing modes instead of expanding it into `\uXXXX`
escapes. Surrogate code units, including lone surrogates and explicit
surrogate-pair strings, remain JSON-escaped so the output is safe to encode as
UTF-8 and pass through protobuf string fields. Unicode is not normalized.
ASCII output, whitespace, custom-object envelopes, and strict/loose type rules
are unchanged; `df_loads` continues to read legacy escaped payloads.

For the synthetic Python value `{"text": "\u0416" * 100000}` (100,000 Cyrillic
characters), the serialized UTF-8 size is **200,012 bytes**, compared with
**600,012 bytes** when ASCII-escaped. This isolates escaping overhead; it does
not measure a complete production request or remove aggregate transport limits.

**Upgrade compatibility:** Serialized bytes change for ordinary non-ASCII text,
even though escaped and literal JSON decode to the same values. Applications
deriving hashes, signatures, IDs, or replay decisions from serialized JSON must
review their byte-dependent logic for upgrades and rollbacks. This change has
not been validated against live hosted backends; provider integration/replay
coverage and real-host staging validation are tracked in
[microsoft/durabletask-python#291](https://github.com/microsoft/durabletask-python/issues/291),
linked from [#371](https://github.com/Azure/azure-functions-python-library/issues/371).

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
