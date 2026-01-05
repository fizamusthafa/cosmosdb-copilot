from azure.cosmos import CosmosClient
from azure.identity import AzureCliCredential

credential = AzureCliCredential()
client = CosmosClient('https://cosmosdb-copilot-demo.documents.azure.com:443/', credential)
container = client.get_database_client('SampleDB').get_container_client('Products')

items = list(container.read_all_items())
updated = 0
for item in items:
    if 'category' in item and item['category'] != item['category'].lower():
        old_cat = item['category']
        # Delete with old partition key, then re-insert with new one
        container.delete_item(item['id'], partition_key=old_cat)
        item['category'] = item['category'].lower()
        container.create_item(item)
        print(f"Updated: {item['name']} - '{old_cat}' -> '{item['category']}'")
        updated += 1

print(f'\nUpdated {updated} items')
