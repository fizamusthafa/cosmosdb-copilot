# CosmosDB Copilot

An AI-powered assistant that lets you query and manage Azure CosmosDB databases using natural language through Microsoft 365 Copilot. This project implements a Declarative Agent that connects to CosmosDB via an MCP (Model Context Protocol) server running as an Azure Function.

## What is CosmosDB Copilot?

CosmosDB Copilot enables you to interact with your Azure CosmosDB databases conversationally. Instead of writing code or using management tools, simply ask questions like:
- "What databases do I have?"
- "Show me all products in the electronics category"
- "List containers in my SampleDB database"
- "Update the price of item ABC123"

The agent understands your intent and executes the appropriate CosmosDB operations through secure, managed tools.

## Features

- **List Databases**: View all databases in your CosmosDB account
- **List Containers**: Explore containers within a specific database
- **Query Items**: Execute SQL queries against your data using natural language
- **Get Items**: Retrieve specific items by ID and partition key
- **Update Items**: Create or update documents in your containers
- **Delete Items**: Remove documents from your containers

## Architecture

This project consists of two main components:

1. **MCP Server** (`mcp-function/`): An Azure Function that exposes CosmosDB operations as MCP tools. It uses Azure Managed Identity for secure authentication to CosmosDB.

2. **Declarative Agent** (`appPackage/`): The M365 Copilot agent configuration that integrates with the MCP server, enabling natural language interactions.

## Prerequisites

To use and deploy CosmosDB Copilot, you need:

- [Azure Developer CLI (azd)](https://aka.ms/azd)
- [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local) >= 4.0.7030
- [Python 3.12](https://www.python.org/downloads/)
- An [Azure CosmosDB account](https://learn.microsoft.com/azure/cosmos-db/)
- [Microsoft 365 Agents Toolkit VS Code Extension](https://aka.ms/teams-toolkit) version 6.0 or higher
- [Microsoft 365 Copilot license](https://learn.microsoft.com/microsoft-365-copilot/extensibility/prerequisites#prerequisites)
- A [Microsoft 365 account for development](https://docs.microsoft.com/microsoftteams/platform/toolkit/accounts)

## Getting Started

### 1. Deploy the MCP Server

The MCP server needs to be deployed to Azure Functions to make it accessible to your Declarative Agent.

```bash
cd mcp-function

# Set your CosmosDB endpoint
azd env set COSMOS_ENDPOINT "https://<your-cosmosdb-account>.documents.azure.com:443/"

# Deploy to Azure
azd up
```

This will:
- Create an Azure resource group
- Deploy the Azure Function (Flex Consumption plan)
- Configure Application Insights for monitoring
- Set up Managed Identity for secure CosmosDB access

After deployment, note the MCP endpoint URL:
```
https://<function-app-name>.azurewebsites.net/runtime/webhooks/mcp/sse?code=<mcp-extension-key>
```

See [mcp-function/README.md](mcp-function/README.md) for detailed deployment instructions.

### 2. Configure the Declarative Agent

1. Open the project in VS Code with the Microsoft 365 Agents Toolkit extension installed

2. Sign in to your M365 developer account through the toolkit

3. Update `appPackage/ai-plugin.json` with your MCP server endpoint URL:
   ```json
   "runtimes": [
     {
       "type": "RemoteMCPServer",
       "spec": {
         "url": "https://<your-function-app>.azurewebsites.net/runtime/webhooks/mcp/sse?code=<your-key>"
       }
     }
   ]
   ```

4. Click "Provision" in the Agents Toolkit to create the app registration

5. Click "Start Debugging" to preview your agent in Copilot

### 3. Test Your Agent

1. Open Microsoft 365 Copilot in Edge or Chrome
2. Find "CosmosDB Copilot" in your available agents
3. Start a conversation with prompts like:
   - "List my databases"
   - "What containers are in SampleDB?"
   - "Show me all products where category is electronics"
   - "Get item with ID ABC123 from the Products container"

## Project Structure

| Folder/File       | Description                                                                                 |
| ----------------- | ------------------------------------------------------------------------------------------- |
| `mcp-function/`   | Azure Function that implements the MCP server with CosmosDB tools. See [mcp-function/README.md](mcp-function/README.md) for details. |
| `appPackage/`     | Declarative Agent configuration files                                                       |
| ├─ `declarativeAgent.json` | Agent definition with name, description, and conversation starters                |
| ├─ `ai-plugin.json` | MCP server connection, authentication, and function definitions                          |
| ├─ `manifest.json` | Teams/M365 integration manifest                                                           |
| ├─ `instruction.txt` | System prompt that defines the agent's behavior                                         |
| `.vscode/`        | VS Code settings and launch configurations                                                  |
| ├─ `mcp.json`     | Local MCP server configuration for development                                              |
| `env/`            | Environment files for different deployment stages                                            |
| `m365agents.yml`  | Defines provisioning and deployment lifecycle for the agent                                 |

## Available CosmosDB Operations

The MCP server exposes these tools that can be invoked through natural language:

| Tool | Description | Example Prompt |
|------|-------------|----------------|
| `list_databases` | List all databases in your CosmosDB account | "What databases do I have?" |
| `list_containers` | List containers in a specific database | "Show me containers in SampleDB" |
| `query_items` | Execute SQL queries against containers | "Find all products with price > 100" |
| `get_item` | Retrieve a specific item by ID and partition key | "Get item ABC123 from Products" |
| `update_item` | Insert or update an item (upsert) | "Add a new product with name Laptop" |
| `delete_item` | Delete an item by ID and partition key | "Delete item ABC123 from Products" |

## Local Development

For local development and testing:

1. Start Azurite (Azure Storage emulator):
   ```bash
   docker run -p 10000:10000 -p 10001:10001 -p 10002:10002 mcr.microsoft.com/azure-storage/azurite
   ```

2. Configure your local settings in `mcp-function/src/local.settings.json`:
   ```json
   {
     "Values": {
       "COSMOS_ENDPOINT": "https://<your-account>.documents.azure.com:443/",
       "AZURE_CLIENT_ID": "<your-managed-identity-client-id>"
     }
   }
   ```

3. Run the function locally:
   ```bash
   cd mcp-function/src
   pip install -r requirements.txt
   func start
   ```

4. Test with MCP Inspector:
   ```bash
   npx @modelcontextprotocol/inspector
   ```
   Connect to: `http://0.0.0.0:7071/runtime/webhooks/mcp/sse`

## Security

- **Authentication**: The MCP server uses Azure Function-level authentication with function keys
- **CosmosDB Access**: Uses Azure Managed Identity for secure, credential-free access to CosmosDB
- **No Credentials**: No database keys or secrets are stored in code or configuration files

## Troubleshooting

### View Azure Function Logs
```bash
az webapp log tail --name <function-app-name> --resource-group <resource-group>
```

### Check Function Status
```bash
az functionapp show --name <function-app-name> --resource-group <resource-group> --query "state" -o tsv
```

### Agent Not Appearing in Copilot
- Ensure your M365 Copilot license is active
- Verify the agent is provisioned in the Agents Toolkit
- Check that the MCP server endpoint is accessible

## Learn More

### Microsoft 365 Copilot & Declarative Agents
- [Microsoft 365 Copilot Extensibility Overview](https://learn.microsoft.com/microsoft-365-copilot/extensibility/)
- [Build Declarative Agents with Agents Toolkit](https://learn.microsoft.com/microsoft-365-copilot/extensibility/build-declarative-agents)
- [Declarative Agents Overview](https://learn.microsoft.com/microsoft-365-copilot/extensibility/overview-declarative-agent)
- [Microsoft 365 Agents Toolkit](https://learn.microsoft.com/microsoft-365/developer/overview-m365-agents-toolkit)
- [Add Plugins to Declarative Agents](https://learn.microsoft.com/microsoft-365-copilot/extensibility/overview-api-plugins)

### Model Context Protocol (MCP)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Architecture & Concepts](https://modelcontextprotocol.io/docs/learn/architecture)

### Azure CosmosDB
- [Azure CosmosDB Documentation](https://learn.microsoft.com/azure/cosmos-db/)
- [CosmosDB SQL Query Reference](https://learn.microsoft.com/azure/cosmos-db/nosql/query/)

### Training Resources
- [Build Your First Declarative Agent - Training Module](https://learn.microsoft.com/training/modules/copilot-declarative-agents-build-your-first/)

## Clean Up

To remove all deployed resources:

```bash
cd mcp-function
azd down
```

## Contributing

This project is an example implementation. Feel free to fork and customize it for your specific CosmosDB use cases.

## License

See LICENSE file for details.
