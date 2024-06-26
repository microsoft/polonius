# Project Polonius

This is a sample flask app to demonstrate using Azure OpenAI with Semantic Kernel to summarize and classify the severity of incoming trauma patients.

## Azure Architecture
![azure architecture diagram](./docs/azure-architecture.drawio.png)

## Pre-requisites
- Azure CLI (az)
- Azure Developer CLI (azd)
- Docker Desktop (for devcontainer) - OR - local python dev environment
- Azure OpenAI (or use `azd provision` to create)

## Getting Started
1. Clone this repo
1. Rename [src/.env.example](src/.env.example) to `.env`
1. Update `.env` file with your configuration values
1. Run locally with debugger

## Deploy to Azure
1. Deploy to Azure with `azd up`

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
