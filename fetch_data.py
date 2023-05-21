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

def fetch_data(type, category):
    base_url = "https://serverjars.com/api/"
    url = f"{base_url}fetchAll/{type}/{category}"
    response = requests.get(url)
    json_data = response.json()
    # Create the directory if it does not exist
    os.makedirs(os.path.join('minecraftversions', type, category), exist_ok=True)

    # Extract the hashes (md5) and save them to a file
    hashes = [item.get('md5') for item in json_data.get('response', []) if item.get('md5')]
    with open(os.path.join('minecraftversions', type, category, 'hashes.txt'), 'w') as f:
        for hash in hashes:
            f.write(hash + '\n')

    return json_data


def download_file(type, category, version, api_hash):
    file_path = os.path.join('minecraftversions', type, category, f"{version}.jar")
    hash_file_path = os.path.join('minecraftversions', type, category, 'hashes.txt')

    # If the hash file exists and the current file's hash is in the hash file, skip the download.
    if os.path.exists(hash_file_path):
        with open(hash_file_path, 'r') as f:
            hashes = [line.strip() for line in f]
        if api_hash in hashes:
            print(f"File {file_path} already exists and has the same hash, skipping download.")
            return

    download_base_url = "https://serverjars.com/api/"
    url = f"{download_base_url}fetchJar/{type}/{category}/{version}"
    response = requests.get(url)
    if response.status_code == 200:
        # Create the directory if it does not exist
        os.makedirs(f'minecraftversions/{type}/{category}', exist_ok=True)
        # Write the version into the directory
        with open(file_path, 'wb') as outfile:
            outfile.write(response.content)
        print(f"File successfully downloaded to {file_path}")
    else:
        print(f"Failed to download version {version}.")

def write_to_file(json_data, type, category):
    # Write the version into the directory
    with open(os.path.join('minecraftversions', type, category, f"{category}.json"), 'w') as outfile:
        json.dump(json_data, outfile)
    print(f"Data successfully written to minecraftversions/{type}/{category}/{category}.json")

if __name__ == "__main__":
    for type, categories in categories.items():
        for category in categories:
            data = fetch_data(type=type, category=category)
            write_to_file(data, type=type, category=category)
            for item in data.get('response', []):
                version = item.get('version')
                api_hash = item.get('md5')  # Get the hash (md5) from the API response
                if version and api_hash:
                    download_file(type=type, category=category, version=version, api_hash=api_hash)
