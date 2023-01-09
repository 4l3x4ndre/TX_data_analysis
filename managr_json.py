import json
import os


def main():

    # Get all list of dir
    dir_names = [name for name in os.listdir('../../dir_process/')]

    with open("../Database_TangibleDataV3.json", 'r+', encoding='utf8') as file:
        # Convert file to JSON
        data = json.loads(file.read())

        for dir_name in dir_names:

            # Get images from OS
            names = [name.split(".png")[0] for name in os.listdir('../../dir_process/' + dir_name)]

            # Select items (according to their names) to add Type propriety
            for item in data:
                if item["id"] in names:
                    item["Type"] = dir_name

    with open('new_file.json', 'w') as f:
        json.dump(data, f, indent=4)


main()
