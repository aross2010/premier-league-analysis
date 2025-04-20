import csv
import os


def write_table_to_csv(data, filename):
    if not data: return 

    data_fields = data[0].keys()

    with open(filename, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=data_fields)
        writer.writeheader()
        writer.writerows(data)

    print(f"Data written to {filename} successfully.")
