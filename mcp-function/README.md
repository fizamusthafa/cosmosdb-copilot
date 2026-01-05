# CosmosDB MCP Server for Azure Functions

This is an MCP (Model Context Protocol) server that exposes CosmosDB tools for use with M365 Copilot declarative agents.

## Tools Available

| Tool | Description |
|------|-------------|
| `list_databases` | List all databases in the CosmosDB account |
| `list_containers` | List all containers in a specific database |
| `query_items` | Execute a SQL query against a container |
| `get_item` | Retrieve a single item by ID and partition key |
| `create_item` | Create a new item in a container |
| `delete_item` | Delete an item from a container |

## Prerequisites

- [Azure Developer CLI (azd)](https://aka.ms/azd)
- [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local) >= 4.0.7030
- [Python 3.12](https://www.python.org/downloads/)
- An Azure CosmosDB account

## Quick Start

### 1. Set up your environment

```bash
cd mcp-function

# Set your CosmosDB credentials
azd env set COSMOS_ENDPOINT "https://<your-cosmosdb-account>.documents.azure.com:443/"
azd env set COSMOS_KEY "<your-cosmosdb-key>"
```

### 2. Deploy to Azure

```bash
azd up
```

This will:
- Create an Azure resource group
- Deploy an Azure Functions app (Flex Consumption plan)
- Configure Application Insights for monitoring
- Set up the MCP server endpoint

### 3. Get your MCP endpoint

After deployment, get the MCP endpoint URL:

```bash
# Get the function app name
az functionapp list --resource-group <your-resource-group> --query "[0].name" -o tsv

# Get the MCP system key
az functionapp keys list --resource-group <your-resource-group> --name <function-app-name> --query "systemKeys.mcp_extension" -o tsv
```

Your MCP endpoint will be:
```
https://<function-app-name>.azurewebsites.net/runtime/webhooks/mcp/sse?code=<mcp-extension-key>
```

## Local Development

### 1. Start Azurite (storage emulator)

```bash
docker run -p 10000:10000 -p 10001:10001 -p 10002:10002 mcr.microsoft.com/azure-storage/azurite
```

### 2. Update local.settings.json

Edit `src/local.settings.json` and set your CosmosDB credentials:

```json
{
  "Values": {
    "COSMOS_ENDPOINT": "https://<your-account>.documents.azure.com:443/",
    "COSMOS_KEY": "<your-key>"
  }
}
```

### 3. Run the function locally

```bash
cd src
pip install -r requirements.txt
func start
```

### 4. Test with MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```

Connect to: `http://0.0.0.0:7071/runtime/webhooks/mcp/sse`

## Using with M365 Copilot Declarative Agent

After deploying, use the Microsoft 365 Agents Toolkit in VS Code:

1. Open your declarative agent project
2. Choose **Add Action → Start with an MCP server**
3. Enter your MCP endpoint URL with the key
4. Select the CosmosDB tools you want to include
5. Configure authentication (if needed)
6. Provision and test your agent

## Clean Up

```bash
azd down
```

## Troubleshooting

### View logs
```bash
az webapp log tail --name <function-app-name> --resource-group <resource-group>
```

### Check function status
```bash
az functionapp show --name <function-app-name> --resource-group <resource-group> --query "state" -o tsv
```
