import requests


framework_name = "pandas"
response = requests.get("http://localhost:5003/frameworks/by-name/" + framework_name)

framework_item_ids = [item for item in response.json()["framework_items"]]
# print(framework_item_ids)

framework_items = []
for id in framework_item_ids:
    response = requests.get("http://localhost:5003/framework_items/" + str(id))
    # print(response.json())
    framework_items.append(response.json())

# print(framework_items[0]['description'])

response = requests.get("http://localhost:5003/llms/by-name/llama:7b")
llm = response.json()
print(llm)