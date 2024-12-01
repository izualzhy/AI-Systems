#!/usr/bin/env python
# coding=utf-8

from transformers import pipeline

if __name__ == '__main__':
    print(pipeline('sentiment-analysis') ('I hate you'))