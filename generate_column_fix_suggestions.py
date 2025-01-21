from langchain_ollama import OllamaLLM
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

    # Extract the JSON portion of the response in case the model messes up
    try:
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)  # Extracted JSON string
            fixed_dict = json.loads(json_str)  # Convert to Python dictionary
            return fixed_dict
        else:
            print("No valid JSON object found in the response.")
            return None
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:", e)
        return None

### Example Usage: test the fix_dictionary
def test_fix_dictionary():
    """
    Calls the `fix_dictionary` function with dummy data for testing.
    """
    # Dummy data
    raw_data = {
        "1": "German",
        "2": "Deutsch",
        "3": "Hungarian",
        "4": "germn",
        "5": "ungarisc",
        "6": "german",
        "7": "goblghgj"
    }
    valid_nationalities = ["German", "Hungarian", "Polish"]

    # Call the function to fix the dictionary
    fixed_dict = fix_dictionary(raw_data, valid_nationalities)

    # Print the result
    print("Fixed Dictionary:", fixed_dict)

# Call the test function
test_fix_dictionary()