import os
import json
import requests

categories = {
    "vanilla": ["vanilla", "snapshot"],
    "servers": ["paper", "purpur", "sponge"],
    "proxies": ["waterfall", "bungeecord", "velocity"],
    "modded": ["mohist", "fabric", "forge", "catserver"],
    "bedrock": ["pocketmine"],
}

def fetch_data(category, type):
    base_url = "https://serverjars.com/api/"
    url = f"{base_url}fetchAll/{category}/{type}"
    response = requests.get(url)
    json_data = response.json()
    return json_data

def write_to_file(json_data, filename):
    # Create the directory if it does not exist
    os.makedirs('minecraftversions', exist_ok=True)
    # Write the file into the directory
    with open(os.path.join('minecraftversions', filename), 'w') as outfile:
        json.dump(json_data, outfile)
    print(f"Data successfully written to minecraftversions/{filename}")

if __name__ == "__main__":
    for category, types in categories.items():
        for type in types:
            data = fetch_data(category=category, type=type)
            write_to_file(data, filename=f"{category}_{type}.json")
