import pandas as pd
from collections import Counter


def analyze_unique_nationalities(file_path):
    """
    Analyze and list unique nationalities in the dataset
    """
    # Read the Excel file
    df = pd.read_excel(file_path)

    # Get all nationality columns
    nationality_columns = [
        "Nationality",
        "Alternative Nationality 1",
        "Alternative Nationality 2",
        "Inferred Nationality",
    ]

    # Create a set for unique nationalities
    unique_nationalities = set()

    # Process each nationality column
    for col in nationality_columns:
        # Get non-null values and convert to lowercase for consistency
        nationalities = df[col].dropna().astype(str).str.strip().str.lower()
        unique_nationalities.update(nationalities)

    # Remove invalid entries
    invalid_entries = {"", "nan", "//", " "}
    unique_nationalities = unique_nationalities - invalid_entries

    # Sort alphabetically
    sorted_nationalities = sorted(unique_nationalities)

    # Print results
    print("\nUNIQUE NATIONALITIES FOUND IN DATASET")
    print("====================================")
    print(f"Total unique values: {len(sorted_nationalities)}")
    print("\nAll unique values (alphabetically):")
    print("----------------------------------")
    for i, nat in enumerate(sorted_nationalities, 1):
        print(f"{i}. {nat}")

    # Save to file
    with open("unique_nationalities.txt", "w", encoding="utf-8") as f:
        f.write("UNIQUE NATIONALITIES IN DATASET\n")
        f.write("==============================\n\n")
        for i, nat in enumerate(sorted_nationalities, 1):
            f.write(f"{i}. {nat}\n")

    print(f"\nList saved to 'unique_nationalities.txt'")


def main():
    try:
        print("Analyzing unique nationalities in the dataset...")
        analyze_unique_nationalities("data.xlsx")

    except FileNotFoundError:
        print("Error: data.xlsx file not found!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
