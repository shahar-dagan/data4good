from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained("t5-base")
model = T5ForConditionalGeneration.from_pretrained("t5-base")

def ask_T5(input_text):
    input_ids = tokenizer.encode(input_text, return_tensors="pt")

    outputs = model.generate(input_ids)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return result


print()
# print(ask_T5("translate English to German: Hello World"))
result = ask_T5(
    """question answering: 
context: T / D 410 029 Name : LISCHNER Eva ge . SKOWRONEK verw . GEFEN BD : 14.11.191 . Warschau / Polen Nat : isr./poln; Sept. 39 Ende 1940 ZAL . Warschau Ende 40 Apr. 43 Gh . Warschau 8 5. 1945 bei Warschau befreit 
question: What is the name of the spouse?"""
)

print(ask_T5(
    f"translate german to english: {result}"
))



# from transformers import T5ForConditionalGeneration, AutoTokenizer

# path_to_model = "ai-forever/T5-large-spell"

# model = T5ForConditionalGeneration.from_pretrained(path_to_model)
# tokenizer = AutoTokenizer.from_pretrained(path_to_model)
# prefix = "grammar: "


# def correct_sentence(misspelling):
#     # sentence = "If you bought something goregous, you well be very happy."
#     # sentence = "The quixk borwn fox jumped over the lazy dog"
#     sentence = prefix + misspelling

#     encodings = tokenizer(sentence, return_tensors="pt")
#     generated_tokens = model.generate(**encodings)
#     answer = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
#     return answer[0]

# print("Enter misspelled sentence")
# while True:
#     print(correct_sentence(input(">")))

# # ["If you bought something gorgeous, you will be very happy."]
