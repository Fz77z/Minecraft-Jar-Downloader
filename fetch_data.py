import os
import json
import requests

BASE_URL = "https://serverjars.com/api/"
DIRECTORY_PATH = 'minecraftversions'

categories = {
    "vanilla": ["vanilla", "snapshot"],
    "servers": ["paper", "purpur", "sponge"],
    "proxies": ["waterfall", "bungeecord", "velocity"],
    "modded": ["mohist", "fabric", "forge", "catserver"],
    "bedrock": ["pocketmine"],
}

def create_directory(type, category):
    try:
        os.makedirs(os.path.join(DIRECTORY_PATH, type, category), exist_ok=True)
    except OSError as e:
        print(f"Error creating directory: {e}")

def get_filepath(type, category, filename):
    return os.path.join(DIRECTORY_PATH, type, category, filename)

def fetch_data(type, category):
    url = f"{BASE_URL}fetchAll/{type}/{category}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def write_hashes_to_file(hashes, filepath):
    try:
        with open(filepath, 'w') as f:
            for hash in hashes:
                f.write(hash + '\n')
    except IOError as e:
        print(f"Error writing hashes to file: {e}")

def get_hashes_from_file(filepath):
    try:
        with open(filepath, 'r') as f:
            return [line.strip() for line in f]
    except IOError as e:
        print(f"Error reading hashes from file: {e}")
        return []

def write_json_to_file(json_data, filepath):
    try:
        with open(filepath, 'w') as outfile:
            json.dump(json_data, outfile)
    except IOError as e:
        print(f"Error writing JSON to file: {e}")

def download_file(type, category, version, api_hash):
    filepath = get_filepath(type, category, f"{version}.jar")
    hash_filepath = get_filepath(type, category, 'hashes.txt')

    # Check if .jar file already exists
    if os.path.exists(filepath):
        if os.path.exists(hash_filepath):
            hashes = get_hashes_from_file(hash_filepath)
            if api_hash in hashes:
                print(f"File {filepath} already exists and has the same hash, skipping download.")
                return
        else:
            print(f"File {filepath} already exists but no hash file found. Please check manually.")
            return

    # If .jar file does not exist, download it
    url = f"{BASE_URL}fetchJar/{type}/{category}/{version}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        create_directory(type, category)
        with open(filepath, 'wb') as outfile:
            outfile.write(response.content)
        print(f"File successfully downloaded to {filepath}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")


def main():
    for type, categories_list in categories.items():
        for category in categories_list:
            data = fetch_data(type=type, category=category)
            if data is None:
                continue
            create_directory(type, category)
            
            hashes = [item.get('md5') for item in data.get('response', []) if item.get('md5')]
            write_hashes_to_file(hashes, get_filepath(type, category, 'hashes.txt'))

            write_json_to_file(data, get_filepath(type, category, f"{category}.json"))
            print(f"Data successfully written to {get_filepath(type, category, f'{category}.json')}")
            
            for item in data.get('response', []):
                version = item.get('version')
                api_hash = item.get('md5')
                if version and api_hash:
                    download_file(type=type, category=category, version=version, api_hash=api_hash)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
