import requests
import json

def prompt_ollama(model_name, prompt):
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model_name,
        "prompt": prompt
    }

    try:
        # Use a streaming request
        with requests.post(url, headers=headers, data=json.dumps(data), stream=True) as response:
            if response.status_code == 200:
                # Process the response line-by-line
                for line in response.iter_lines():
                    if line:
                        try:
                            # Parse each JSON object
                            json_data = json.loads(line.decode('utf-8'))
                            print("Ollama Response:", json_data.get("response", ""))
                        except json.JSONDecodeError as e:
                            print(f"JSON Decode Error: {e}")
            else:
                print(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Failed to connect to Ollama server: {e}")

# Example usage
model_name = "llama3.2:latest"  # Use the correct model name
user_prompt = "What is the capital of France?"
prompt_ollama(model_name, user_prompt)
