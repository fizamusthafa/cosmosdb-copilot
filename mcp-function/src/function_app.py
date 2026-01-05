import json
import logging
import os
from azure.cosmos import CosmosClient, exceptions
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# CosmosDB connection settings - these will be set via environment variables
COSMOS_ENDPOINT = os.environ.get("COSMOS_ENDPOINT", "")
COSMOS_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID", "")  # User-assigned managed identity client ID


def get_cosmos_client():
    """Get a CosmosDB client instance using Managed Identity."""
    if not COSMOS_ENDPOINT:
        raise ValueError("COSMOS_ENDPOINT environment variable must be set")
    
    # Use ManagedIdentityCredential with specific client ID if provided, otherwise DefaultAzureCredential
    if COSMOS_CLIENT_ID:
        credential = ManagedIdentityCredential(client_id=COSMOS_CLIENT_ID)
    else:
        credential = DefaultAzureCredential()
    
    return CosmosClient(COSMOS_ENDPOINT, credential=credential)


class ToolProperty:
    """Helper class to define MCP tool properties."""
    def __init__(self, property_name: str, property_type: str, description: str, required: bool = True):
        self.propertyName = property_name
        self.propertyType = property_type
        self.description = description
        self.required = required

    def to_dict(self):
        return {
            "propertyName": self.propertyName,
            "propertyType": self.propertyType,
            "description": self.description,
        }


# Define tool properties for each CosmosDB operation
list_databases_properties = json.dumps([])

list_containers_properties = json.dumps([
    ToolProperty("database_name", "string", "The name of the database to list containers from.").to_dict()
])

query_items_properties = json.dumps([
    ToolProperty("database_name", "string", "The name of the database.").to_dict(),
    ToolProperty("container_name", "string", "The name of the container to query.").to_dict(),
    ToolProperty("query", "string", "The SQL query to execute (e.g., 'SELECT * FROM c WHERE c.category = \"electronics\"').").to_dict(),
])

get_item_properties = json.dumps([
    ToolProperty("database_name", "string", "The name of the database.").to_dict(),
    ToolProperty("container_name", "string", "The name of the container.").to_dict(),
    ToolProperty("item_id", "string", "The ID of the item to retrieve.").to_dict(),
    ToolProperty("partition_key", "string", "The partition key value for the item.").to_dict(),
])

delete_item_properties = json.dumps([
    ToolProperty("database_name", "string", "The name of the database.").to_dict(),
    ToolProperty("container_name", "string", "The name of the container.").to_dict(),
    ToolProperty("item_id", "string", "The ID of the item to delete.").to_dict(),
    ToolProperty("partition_key", "string", "The partition key value for the item.").to_dict(),
])

upsert_item_properties = json.dumps([
    ToolProperty("database_name", "string", "The name of the database.").to_dict(),
    ToolProperty("container_name", "string", "The name of the container.").to_dict(),
    ToolProperty("item", "string", "The JSON string representing the item to upsert (insert or update).").to_dict(),
])


# MCP Tool: List all databases
@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="list_databases",
    description="List all databases in the CosmosDB account.",
    toolProperties=list_databases_properties,
)
def list_databases(context) -> str:
    """List all databases in the CosmosDB account."""
    try:
        client = get_cosmos_client()
        databases = list(client.list_databases())
        database_names = [db['id'] for db in databases]
        logging.info(f"Listed {len(database_names)} databases")
        return json.dumps({
            "success": True,
            "databases": database_names,
            "count": len(database_names)
        })
    except Exception as e:
        logging.error(f"Error listing databases: {str(e)}")
        return json.dumps({"success": False, "error": str(e)})


# MCP Tool: List containers in a database
@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="list_containers",
    description="List all containers in a specific CosmosDB database.",
    toolProperties=list_containers_properties,
)
def list_containers(context) -> str:
    """List all containers in a specific database."""
    try:
        content = json.loads(context)
        database_name = content["arguments"]["database_name"]
        
        client = get_cosmos_client()
        database = client.get_database_client(database_name)
        containers = list(database.list_containers())
        container_names = [c['id'] for c in containers]
        
        logging.info(f"Listed {len(container_names)} containers in database '{database_name}'")
        return json.dumps({
            "success": True,
            "database": database_name,
            "containers": container_names,
            "count": len(container_names)
        })
    except exceptions.CosmosResourceNotFoundError:
        return json.dumps({"success": False, "error": f"Database '{database_name}' not found"})
    except Exception as e:
        logging.error(f"Error listing containers: {str(e)}")
        return json.dumps({"success": False, "error": str(e)})


# MCP Tool: Query items in a container
@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="query_items",
    description="Execute a SQL query against a CosmosDB container to retrieve items.",
    toolProperties=query_items_properties,
)
def query_items(context) -> str:
    """Execute a SQL query against a container."""
    try:
        content = json.loads(context)
        database_name = content["arguments"]["database_name"]
        container_name = content["arguments"]["container_name"]
        query = content["arguments"]["query"]
        
        client = get_cosmos_client()
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)
        
        # Execute query with cross-partition enabled
        items = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        logging.info(f"Query returned {len(items)} items from '{database_name}/{container_name}'")
        return json.dumps({
            "success": True,
            "database": database_name,
            "container": container_name,
            "query": query,
            "items": items,
            "count": len(items)
        })
    except exceptions.CosmosResourceNotFoundError as e:
        return json.dumps({"success": False, "error": f"Resource not found: {str(e)}"})
    except exceptions.CosmosHttpResponseError as e:
        return json.dumps({"success": False, "error": f"Query error: {str(e)}"})
    except Exception as e:
        logging.error(f"Error querying items: {str(e)}")
        return json.dumps({"success": False, "error": str(e)})


# MCP Tool: Get a single item by ID
@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_item",
    description="Retrieve a single item from a CosmosDB container by its ID and partition key.",
    toolProperties=get_item_properties,
)
def get_item(context) -> str:
    """Get a single item by ID and partition key."""
    try:
        content = json.loads(context)
        database_name = content["arguments"]["database_name"]
        container_name = content["arguments"]["container_name"]
        item_id = content["arguments"]["item_id"]
        partition_key = content["arguments"]["partition_key"]
        
        client = get_cosmos_client()
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)
        
        item = container.read_item(item=item_id, partition_key=partition_key)
        
        logging.info(f"Retrieved item '{item_id}' from '{database_name}/{container_name}'")
        return json.dumps({
            "success": True,
            "item": item
        })
    except exceptions.CosmosResourceNotFoundError:
        return json.dumps({"success": False, "error": f"Item '{item_id}' not found"})
    except Exception as e:
        logging.error(f"Error getting item: {str(e)}")
        return json.dumps({"success": False, "error": str(e)})


# MCP Tool: Delete an item
@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="delete_item",
    description="Delete an item from a CosmosDB container by its ID and partition key.",
    toolProperties=delete_item_properties,
)
def delete_item(context) -> str:
    """Delete an item from a container."""
    try:
        content = json.loads(context)
        database_name = content["arguments"]["database_name"]
        container_name = content["arguments"]["container_name"]
        item_id = content["arguments"]["item_id"]
        partition_key = content["arguments"]["partition_key"]
        
        client = get_cosmos_client()
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)
        
        container.delete_item(item=item_id, partition_key=partition_key)
        
        logging.info(f"Deleted item '{item_id}' from '{database_name}/{container_name}'")
        return json.dumps({
            "success": True,
            "message": f"Item '{item_id}' deleted successfully"
        })
    except exceptions.CosmosResourceNotFoundError:
        return json.dumps({"success": False, "error": f"Item '{item_id}' not found"})
    except Exception as e:
        logging.error(f"Error deleting item: {str(e)}")
        return json.dumps({"success": False, "error": str(e)})


# MCP Tool: Upsert an item (insert or update)
@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="update_item",
    description="Update or insert an item in a CosmosDB container. Use this to update an existing item or create a new one. If an item with the same ID exists, it will be replaced with the new data; otherwise, a new item will be created.",
    toolProperties=upsert_item_properties,
)
def upsert_item(context) -> str:
    """Upsert an item in a container (insert or replace if exists)."""
    try:
        content = json.loads(context)
        database_name = content["arguments"]["database_name"]
        container_name = content["arguments"]["container_name"]
        item_str = content["arguments"]["item"]
        
        # Parse the item JSON string
        item = json.loads(item_str)
        
        client = get_cosmos_client()
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)
        
        upserted_item = container.upsert_item(body=item)
        
        logging.info(f"Upserted item in '{database_name}/{container_name}'")
        return json.dumps({
            "success": True,
            "message": "Item upserted successfully (inserted or updated)",
            "item": upserted_item
        })
    except json.JSONDecodeError:
        return json.dumps({"success": False, "error": "Invalid JSON format for item"})
    except Exception as e:
        logging.error(f"Error upserting item: {str(e)}")
        return json.dumps({"success": False, "error": str(e)})
