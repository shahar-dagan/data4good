from transformers import pipeline
from transformers import AutoModelForMaskedLM, AutoTokenizer

def load_model_and_tokenizer():
    # Load a BERT-based model fine-tuned for masked language modeling
    model_name = "bert-base-uncased"  # You can change this to another BERT model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForMaskedLM.from_pretrained(model_name)
    return tokenizer, model

def correct_spelling(misspelled_text, misspelled_words):
    """
    Correct misspelled words by processing the input as:
    "misspelled: <original sentence>"
    "corrected: <sentence with [MASK]>"
    """
    # Prepare the input text for BERT
    text_correction_template = " ".join(
        word if word not in misspelled_words else "[MASK]"
        for word in misspelled_text.split()
    )

    input_text = f"misspelled: {misspelled_text} [SEP] spell corrected: {text_correction_template}"
    # Create a pipeline for masked language modeling
    fill_mask = pipeline("fill-mask", model=model, tokenizer=tokenizer)

    # Get predictions for the masked token
    predictions = fill_mask(input_text)

    # Use the top prediction to replace [MASK]
    corrected_word = predictions[0]['token_str']

    # Replace [MASK] with the predicted word in the corrected sentence
    corrected_text = input_text.replace("[MASK]", corrected_word)

    return corrected_text

# Load the model and tokenizer
tokenizer, model = load_model_and_tokenizer()

# Input text with a misspelled word

# Perform spelling correction
misspelled_text="I went to the shop because my laptop changing cable was broken"
misspelled_words=["changing"]

corrected_text = correct_spelling(
    misspelled_text,
    misspelled_words
)

print("Model input:\n", misspelled_text, "\n")
print("Model output:\n", corrected_text)
