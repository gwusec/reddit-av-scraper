import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Load model directly
tokenizer = AutoTokenizer.from_pretrained("lazyghost/bert-large-uncased-Adult-Text-Classifier")
model = AutoModelForSequenceClassification.from_pretrained("lazyghost/bert-large-uncased-Adult-Text-Classifier")


# Example use-case
text = "Get your spirits up with world-class alcoholic beverages"

inputs = tokenizer(text, return_tensors="pt") #pytorch 
outputs = model(**inputs)

probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
predicted_class_id = torch.argmax(probs, dim=-1).item()
predicted_class_label = model.config.id2label[predicted_class_id]

print(f"Text: {text}")
print(f"Predicted class: {predicted_class_label}")
print(f"Probabilities: {probs}")
