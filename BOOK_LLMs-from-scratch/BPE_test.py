#!/usr/bin/env python
# coding=utf-8


from importlib.metadata import version
import tiktoken
print("tiktoken version:", version("tiktoken"))

tokenizer = tiktoken.get_encoding("gpt2")

text = (
    "Hello, do you like tea? <|endoftext|> In the sunlit terraces"
    "of someunknownPlace."
)
integers = tokenizer.encode(text, allowed_special={"<|endoftext|>"})
print(integers)

strings = tokenizer.decode(integers)
print(strings)

def encode_and_decode(text):
    integers = tokenizer.encode(text)
    print(integers)
    strings = tokenizer.decode(integers)
    print(strings)

encode_and_decode("Hello, do you like tea? I like tea very much.")


with open("./LLMs-from-scratch/ch02/01_main-chapter-code/the-verdict.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

enc_text = tokenizer.encode(raw_text)
print(len(enc_text))

for i in range(0, 10):
    print(f'{enc_text[i]} => {tokenizer.decode([enc_text[i]])}')

# enc_sample = enc_text[50:]
enc_sample = enc_text
context_size = 4
for i in range(1, context_size+1):
    context = enc_sample[:i]
    desired = enc_sample[i]
    print(tokenizer.decode(context), "---->", tokenizer.decode([desired]))