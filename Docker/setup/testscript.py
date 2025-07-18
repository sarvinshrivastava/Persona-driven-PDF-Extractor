from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_id = "tiiuae/falcon-rw-1b"

tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code = True)
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code = True)

print("Welcome to the Phi-4-mini-flash CLI. Type your input and press Enter (Ctrl+C to exit).")

while True:
    try:
        prompt = input(">>> ")
        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=100)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(response)
    except KeyboardInterrupt:
        print("\n[INFO] Exiting...")
        break
