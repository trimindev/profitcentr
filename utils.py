import shutil
import os
import random
import json


def generate_random_number():
    return random.randint(0, 100000)


def copy_and_rename_folder(src_path: str, dest_path: str, new_folder_name: str):
    try:
        # Copy the entire folder to the destination path
        shutil.copytree(src_path, os.path.join(dest_path, new_folder_name))

        # Rename the newly copied folder
        new_folder_path = os.path.join(dest_path, new_folder_name)
        os.rename(os.path.join(dest_path, os.path.basename(src_path)), new_folder_path)

        print(f"Folder copied and renamed successfully to: {new_folder_path}")

        # except shutil.Error as e:
        # print(f"Error copying folder: {e}")
    except OSError as e:
        # print(f"Error: {e}")
        print("")


def rename_folder(path: str, old_name: str, new_name: str):
    try:
        # Construct the full path to the folder
        old_folder_path = os.path.join(path, old_name)

        # Check if the folder exists
        if not os.path.exists(old_folder_path):
            print(f"Error: Folder '{old_folder_path}' does not exist.")
            return

        # Construct the full path to the new folder name
        new_folder_path = os.path.join(path, new_name)

        # Rename the folder
        os.rename(old_folder_path, new_folder_path)

        print(f"Folder renamed successfully to: {new_folder_path}")

    except OSError as e:
        print(f"Error: {e}")


def delete_folder(folder_path: str, folder_name: str):
    try:
        # Construct the full path to the folder
        full_folder_path = os.path.join(folder_path, folder_name)

        # Delete the entire folder
        shutil.rmtree(full_folder_path)
        print(f"Folder deleted successfully: {full_folder_path}")
    except shutil.Error as e:
        print(f"Error deleting folder: {e}")
    except OSError as e:
        print(f"Error: {e}")


def get_folder_path(base_folder_path: str, folder_name: str):
    return os.path.join(base_folder_path, folder_name)


def get_folder_names(directory: str):
    try:
        # Get all entries in the directory
        entries = os.listdir(directory)

        # Filter out only the directories
        folder_names = [
            entry for entry in entries if os.path.isdir(os.path.join(directory, entry))
        ]

        return folder_names
    except OSError as e:
        print(f"Error reading directory {directory}: {e}")
        return []


def replace_item_by_id(json_file, target_id, new_item):
    # Read the JSON file
    with open(json_file, "r") as file:
        data = json.load(file)

    # Find the index of the item with the specified 'name'
    for index, item in enumerate(data):
        if item["id"] == target_id:
            # Replace the item at the found index with the new item
            data[index] = new_item
            break

    # Write the updated data back to the JSON file
    with open(json_file, "w") as file:
        json.dump(data, file, indent=2)


def update_item_id(json_file, target_id, new_id):
    # Read the JSON file
    with open(json_file, "r") as file:
        data = json.load(file)

    # Find and update the item with the specified 'name'
    for item in data:
        if item["id"] == target_id:
            item["id"] = new_id
            break

    # Write the updated data back to the JSON file
    with open(json_file, "w") as file:
        json.dump(data, file, indent=2)


def update_item_name(json_file, target_id, new_name):
    # Read the JSON file
    with open(json_file, "r") as file:
        data = json.load(file)

    # Find and update the item with the specified 'name'
    for item in data:
        if item["id"] == target_id:
            item["name"] = new_name
            break

    # Write the updated data back to the JSON file
    with open(json_file, "w") as file:
        json.dump(data, file, indent=2)
