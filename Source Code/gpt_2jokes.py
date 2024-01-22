# -*- coding: utf-8 -*-
"""GPT-2Jokes.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OXltylpbgmEDM2rR7SFp1RfzdyTdeLAa

# ***Link:*** [Jokes Dataset](https://www.kaggle.com/datasets/abhinavmoudgil95/short-jokes)
"""

from google.colab import drive
drive.mount('/content/drive')

pip install transformers

import pandas as pd
from transformers import GPT2LMHeadModel
from transformers import GPT2Tokenizer
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import Dataset, DataLoader

df = pd.read_csv('/content/drive/My Drive/shortjokes.csv') #Change to Local Directory
print(df.head())

tokenizer = GPT2Tokenizer.from_pretrained('gpt2-medium')
tokenized_data = [tokenizer.encode(joke) for joke in df['Joke']]

class JokesDataset(Dataset):
    def __init__(self, tokenized_data):
        self.tokenized_data = tokenized_data

    def __len__(self):
        return len(self.tokenized_data)

    def __getitem__(self, idx):
        return (torch.tensor(self.tokenized_data[idx]), len(self.tokenized_data[idx]))

from torch.nn.utils.rnn import pad_sequence

def collate_fn(batch):
    batch = sorted(batch, key=lambda x: x[1], reverse=True)

    sequences, lengths = zip(*batch)

    padded_sequences = pad_sequence(sequences, batch_first=True)

    return padded_sequences

train_data, val_data = train_test_split(tokenized_data, test_size=0.1)

train_dataset = JokesDataset(train_data)
val_dataset = JokesDataset(val_data)

train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True, collate_fn=collate_fn)
val_loader = DataLoader(val_dataset, batch_size=8, shuffle=True, collate_fn=collate_fn)

model = GPT2LMHeadModel.from_pretrained('gpt2-medium')

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

model.train()

from transformers import AdamW
optimizer = AdamW(model.parameters(), lr=3e-4)

num_epochs = 3

for epoch in range(num_epochs):
    print(f"Epoch {epoch + 1}/{num_epochs}")

    for idx, batch in enumerate(train_loader):
        inputs = batch.to(device)

        optimizer.zero_grad()

        outputs = model(inputs, labels=inputs)
        loss, logits = outputs[:2]

        loss.backward()
        optimizer.step()

        if idx % 100 == 0:
            print(f"Batch {idx}/{len(train_loader)} - Loss: {loss.item()}")

model.eval()
total_val_loss = 0

with torch.no_grad():
    for batch in val_loader:
        inputs = batch.to(device)

        outputs = model(inputs, labels=inputs)
        loss = outputs[0]

        total_val_loss += loss.item()

avg_val_loss = total_val_loss / len(val_loader)
print(f"Validation Loss: {avg_val_loss}")

model.eval()
prompt_text = "Why did the chicken"
encoded_prompt = tokenizer.encode(prompt_text, add_special_tokens=False, return_tensors="pt").to(device)

output_sequences = model.generate(
    input_ids=encoded_prompt,
    max_length=100,
    temperature=0.7,
    top_k=30,
    top_p=0.9,
    repetition_penalty=1.2,
    do_sample=True,
    num_return_sequences=1
)

generated_sequence = output_sequences[0].tolist()
joke_text = tokenizer.decode(generated_sequence, clean_up_tokenization_spaces=True)

print(joke_text)

num_jokes = 11

output_sequences = model.generate(
    input_ids=encoded_prompt,
    max_length=100,
    temperature=0.7,
    top_k=30,
    top_p=0.9,
    repetition_penalty=1.2,
    do_sample=True,
    num_return_sequences=num_jokes
)

for i, sequence in enumerate(output_sequences):
    joke = tokenizer.decode(sequence, clean_up_tokenization_spaces=True)
    print(f"Joke {i + 1}: {joke}")