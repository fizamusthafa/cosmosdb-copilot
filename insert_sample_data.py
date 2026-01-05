"""Insert sample data into Cosmos DB using Azure Identity"""
from azure.cosmos import CosmosClient, PartitionKey
from azure.identity import AzureCliCredential

# Connection settings
ENDPOINT = "https://cosmosdb-copilot-demo.documents.azure.com:443/"
DATABASE_NAME = "SampleDB"
CONTAINER_NAME = "Products"

# Use Azure CLI credentials for authentication
credential = AzureCliCredential()

# Sample product data
products = [
    {
        "id": "1",
        "name": "Laptop Pro 15",
        "category": "Electronics",
        "price": 1299.99,
        "description": "High-performance laptop with 15-inch display",
        "inStock": True,
        "quantity": 50
    },
    {
        "id": "2",
        "name": "Wireless Mouse",
        "category": "Electronics",
        "price": 29.99,
        "description": "Ergonomic wireless mouse with long battery life",
        "inStock": True,
        "quantity": 200
    },
    {
        "id": "3",
        "name": "USB-C Hub",
        "category": "Electronics",
        "price": 49.99,
        "description": "7-in-1 USB-C hub with HDMI and SD card reader",
        "inStock": True,
        "quantity": 150
    },
    {
        "id": "4",
        "name": "Office Chair",
        "category": "Furniture",
        "price": 299.99,
        "description": "Ergonomic office chair with lumbar support",
        "inStock": True,
        "quantity": 30
    },
    {
        "id": "5",
        "name": "Standing Desk",
        "category": "Furniture",
        "price": 599.99,
        "description": "Electric height-adjustable standing desk",
        "inStock": False,
        "quantity": 0
    },
    {
        "id": "6",
        "name": "Monitor Stand",
        "category": "Furniture",
        "price": 79.99,
        "description": "Adjustable monitor stand with storage drawer",
        "inStock": True,
        "quantity": 75
    },
    {
        "id": "7",
        "name": "Mechanical Keyboard",
        "category": "Electronics",
        "price": 149.99,
        "description": "RGB mechanical keyboard with Cherry MX switches",
        "inStock": True,
        "quantity": 100
    },
    {
        "id": "8",
        "name": "Desk Lamp",
        "category": "Lighting",
        "price": 45.99,
        "description": "LED desk lamp with adjustable brightness",
        "inStock": True,
        "quantity": 120
    },
    {
        "id": "9",
        "name": "Webcam HD",
        "category": "Electronics",
        "price": 89.99,
        "description": "1080p HD webcam with built-in microphone",
        "inStock": True,
        "quantity": 80
    },
    {
        "id": "10",
        "name": "Notebook Set",
        "category": "Office Supplies",
        "price": 15.99,
        "description": "Pack of 5 lined notebooks",
        "inStock": True,
        "quantity": 500
    }
]

def main():
    # Initialize the Cosmos client with Azure Identity
    client = CosmosClient(ENDPOINT, credential=credential)
    
    # Get database and container
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)
    
    print(f"Inserting {len(products)} products into {DATABASE_NAME}/{CONTAINER_NAME}...")
    
    # Insert each product
    for product in products:
        try:
            container.upsert_item(product)
            print(f"  ✓ Inserted: {product['name']}")
        except Exception as e:
            print(f"  ✗ Failed to insert {product['name']}: {e}")
    
    print("\nDone! Sample data inserted successfully.")
    
    # Verify by querying
    print("\nVerifying data with a sample query...")
    query = "SELECT * FROM c WHERE c.category = 'Electronics'"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    print(f"Found {len(items)} electronics products.")

if __name__ == "__main__":
    main()
