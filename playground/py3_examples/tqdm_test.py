#!/usr/bin/env python
# coding=utf-8
import time

from tqdm import tqdm

pbar = tqdm(total=100)

for i in range(10):
    pbar.update(10)
    time.sleep(10)

pbar.close()