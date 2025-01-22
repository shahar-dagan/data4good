import sys
import os

# Add the current directory to the module search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from langchain_ollama import OllamaLLM
from anomaly import HolocaustRecordValidator
import json
import re

### Suggestion generation function:
# fix_dictionary: Fix the dictionary using the model (gemma:7b)
# accepts: raw_data(string list); valid_nationalities(dictionary), model_name(optional, string)
def fix_dictionary(raw_data, valid_nationalities, model_name="gemma:7b"):
    """
    Takes a dictionary to be corrected and a list of valid values. 
    Uses an Ollama model to correct the dictionary values and returns the fixed dictionary.
    """
    # Convert the dictionary to a key-value string format:
    raw_data_str = ', '.join([f'"{key}": "{value}"' for key, value in raw_data.items()])

    # Prompt construction:
    prompt = f"""
    Convert each of the provided nationalities in the JSON object to one of the valid nationalities: {', '.join(valid_nationalities)}.
    Return the results as a JSON object where the keys match the input keys, with no additional formatting or explanation.

    Input: {{{raw_data_str}}}
    Output:
    """

    # Model prompt
    model = OllamaLLM(model=model_name)
    response = model(prompt)
    print(response)

    # Extract the JSON portion of the response in case the model messes up
    try:
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)  # Extracted JSON string
            fixed_dict = json.loads(json_str)  # Convert to Python dictionary
            return fixed_dict
        else:
            print("No valid JSON object found in the response.")
            print(response)
            return None
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:", e)
        return None

def extract_invalid_nationality(file_path):
    """
    Extracts a dictionary of fields with issue type 'invalid_nationality',
    matching 'TD' to 'Current Value'.

    Args:
        file_path (str): Path to the Excel file.

    Returns:
        dict: Dictionary with 'TD' as keys and 'Current Value' as values.
    """
    # Load the Excel file into a DataFrame
    df = pd.read_excel(file_path)

    # Filter rows with issue type 'invalid_nationality'
    filtered_df = df[df['Issue Type'] == 'invalid_nationality']

    # Create a dictionary with 'TD' as keys and 'Current Value' as values
    result_dict = filtered_df.set_index('TD')['Current Value'].to_dict()

    return result_dict

def split_dictionary(input_dict, chunk_size):
    items = list(input_dict.items())
    return [dict(items[i:i + chunk_size]) for i in range(0, len(items), chunk_size)]

def generate_suggestions_file(file_path, valid_nationalities):
    """
    Creates a new file with a 'Suggestions' column based on fixed nationalities, processing in chunks.

    Args:
        file_path (str): Path to the anomaly report Excel file.
        valid_nationalities (list): List of valid nationalities.

    Returns:
        None
    """
    # Read the original Excel file
    df = pd.read_excel(file_path)

    # Extract invalid nationalities
    print("Extracting invalid nationalities...")
    invalid_nationalities = extract_invalid_nationality(file_path)
    print(invalid_nationalities)

    if not invalid_nationalities:
        print("No invalid nationalities found.")
        # Add an empty "Suggestions" column and save the new file
        df['Suggestions'] = None
        df.to_excel("anomaly_suggestions.xlsx", index=False)
        print("File saved with no suggestions.")
        return

    # Split the invalid nationalities into smaller chunks
    chunk_size = 20
    chunks = split_dictionary(invalid_nationalities, chunk_size)

    # Initialize an empty dictionary to store all fixed suggestions
    fixed_dict = {}

    # Process each chunk using the model
    print("Fixing invalid nationalities in chunks...")
    for i, chunk in enumerate(chunks):
        if i > 3:
            break
        print(f"Processing chunk {i + 1}/{len(chunks)}...")
        fixed_chunk = fix_dictionary(chunk, valid_nationalities)
        if fixed_chunk:
            fixed_dict.update(fixed_chunk)  # Add the fixed chunk to the main dictionary

    # Add a new column 'Suggestions' to the DataFrame
    df['Suggestions'] = df['TD'].map(fixed_dict)  # Map the fixed nationalities to the corresponding rows

    # Save the updated DataFrame to a new file
    df.to_excel("anomaly_suggestions.xlsx", index=False)
    print("File saved as anomaly_suggestions.xlsx with suggestions added.")

# Example usage
if __name__ == "__main__":
    # File path to the Excel file
    file_path = "anomaly_report.xlsx"

    validator = HolocaustRecordValidator()
    generate_suggestions_file(file_path, validator.valid_nationalities)