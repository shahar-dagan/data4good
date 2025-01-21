import pandas as pd
from collections import Counter


def analyze_unique_religions(file_path):
    """
    Analyze and list unique religions in the dataset
    """
    # Read the Excel file
    df = pd.read_excel(file_path)

    # Get religion column
    religion_column = "Religion"

    # Create a set for unique religions
    unique_religions = set()

    # Get non-null values and convert to lowercase for consistency
    religions = df[religion_column].dropna().astype(str).str.strip().str.lower()
    unique_religions.update(religions)

    # Remove invalid entries
    invalid_entries = {"", "nan", "//", " "}
    unique_religions = unique_religions - invalid_entries

    # Sort alphabetically
    sorted_religions = sorted(unique_religions)

    # Print results
    print("\nUNIQUE RELIGIONS FOUND IN DATASET")
    print("================================")
    print(f"Total unique values: {len(sorted_religions)}")
    print("\nAll unique values (alphabetically):")
    print("----------------------------------")
    for i, rel in enumerate(sorted_religions, 1):
        print(f"{i}. {rel}")

    # Save to file
    with open("unique_religions.txt", "w", encoding="utf-8") as f:
        f.write("UNIQUE RELIGIONS IN DATASET\n")
        f.write("==========================\n\n")
        for i, rel in enumerate(sorted_religions, 1):
            f.write(f"{i}. {rel}\n")

    print(f"\nList saved to 'unique_religions.txt'")


def main():
    try:
        print("Analyzing unique religions in the dataset...")
        analyze_unique_religions("data.xlsx")

    except FileNotFoundError:
        print("Error: data.xlsx file not found!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
