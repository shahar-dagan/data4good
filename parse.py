import pandas as pd
import numpy as np


def load_database(file_path):
    """
    Load and parse the Excel database
    """
    # Read the Excel file
    df = pd.read_excel(file_path)

    # Clean column names (remove leading/trailing whitespace and special characters)
    df.columns = df.columns.str.strip()

    # Create a mapping for the nationality columns as they appear in your Excel file
    column_mapping = {
        "Nationality": "nationality",
        "Alternative Nationality 1": "alternative_nationality_1",
        "Alternative Nationality 2": "alternative_nationality_2",
        "Inferred Nationality": "inferred_nationality",
    }

    # Rename the columns using the mapping
    df = df.rename(columns=column_mapping)

    # Handle missing values
    df = df.replace("", np.nan)

    return df


def analyze_nationalities(df):
    """
    Analyze and count nationalities from all nationality columns
    Returns a dictionary with nationality counts
    """
    # Initialize dictionary to store nationality counts
    nationality_counts = {}

    # Columns to check for nationalities
    nationality_columns = [
        "nationality",
        "alternative_nationality_1",
        "alternative_nationality_2",
        "inferred_nationality",
    ]

    # Process each nationality column
    for col in nationality_columns:
        if col in df.columns:
            # Get non-null values from the column
            nationalities = df[col].dropna()

            # Count each nationality
            for nat in nationalities:
                nat = str(nat).strip()
                if nat:  # Check if nationality is not empty
                    nationality_counts[nat] = nationality_counts.get(nat, 0) + 1

    return nationality_counts


def main():
    try:
        # Load the database
        df = load_database("data.xlsx")

        # Print basic information about the dataset
        print("\nDatabase Summary:")
        print("-----------------")
        print(f"Total number of records: {len(df)}")

        # Analyze nationalities
        nationality_counts = analyze_nationalities(df)

        # Print nationality statistics
        print("\nNationality Distribution:")
        print("------------------------")
        # Sort nationalities by count in descending order
        sorted_nationalities = sorted(
            nationality_counts.items(), key=lambda x: x[1], reverse=True
        )

        for nationality, count in sorted_nationalities:
            print(f"{nationality}: {count} people")

    except FileNotFoundError:
        print("Error: data.xlsx file not found!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
