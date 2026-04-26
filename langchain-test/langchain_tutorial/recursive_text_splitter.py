#!/usr/bin/env python
# coding=utf-8

# https://python.langchain.com/docs/how_to/recursive_text_splitter/

from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load example document
with open("../data/state_of_the_union.txt") as f:
    state_of_the_union = f.read()

text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=100,
    chunk_overlap=20,
    length_function=len,
    is_separator_regex=False,
    separators=['.']
)
texts = text_splitter.create_documents([state_of_the_union])
print(texts[0])
print(texts[1])