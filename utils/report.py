import os
import csv
import parameters

def createReport(folder, output_csv):
    # List all items in the specified folder
    items = sorted(os.listdir(folder))
    counter = 0

    # Create and write to the CSV file
    with open(output_csv, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Project', 'Requirements'])

        for item in items:
            item_path = os.path.join(folder, item)
            requirement = False

            if os.path.isdir(item_path):
                for file in os.listdir(item_path):

                    # Check if the file is a requirements file
                    if 'requirement' in file.lower():
                        requirement = True
                        writer.writerow([item, requirement])
                        break
            
            if requirement:
                counter += 1


    print(f"CSV file '{output_csv}' created successfully.")
    print(f"Number of projects with a requirements file: {counter}/{len(items)}")

if __name__ == "__main__":
    folder = parameters.PROJECTS
    output_csv = parameters.REPORT

    # Call the function
    createReport(folder, output_csv)
