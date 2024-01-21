import json


class Info:
    def __init__(self, path):
        self.path = path

    def add(self, info):
        # Read the JSON file
        with open(self.path, "r") as file:
            data = json.load(file)

        # Append the new item to the list
        data.append(info)

        # Write the updated data back to the JSON file
        with open(self.path, "w") as file:
            json.dump(data, file, indent=2)

    def delete(self, info_id):
        # Read the JSON file
        with open(self.path, "r") as file:
            data = json.load(file)

        # Find and remove the item with the specified 'id'
        for item in data:
            if item["id"] == info_id:
                data.remove(item)
                break

        # Write the updated data back to the JSON file
        with open(self.path, "w") as file:
            json.dump(data, file, indent=2)

    def get_info_by_id(self, info_id):
        # Read the JSON file
        with open(self.path, "r") as file:
            data = json.load(file)

        # Find and return the item with the specified 'id'
        for item in data:
            if item["id"] == info_id:
                return item

        # If the item is not found, return None or raise an exception, depending on your use case
        return None

    def get_all_info(self):
        with open(self.path, "r") as file:
            data = json.load(file)
        return data
