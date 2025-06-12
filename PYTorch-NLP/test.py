#!/usr/bin/env python
# coding=utf-8

import torch

if __name__ == '__main__':
    char_list = ['a', 'b', 'c', 'd', 'e']
    n_chars = len(char_list) + 1  # 加一个UNK

    def title_to_tensor(title):
        tensor = torch.zeros(len(title), 1, n_chars)
        for li, ch in enumerate(title):
            print(f'li:{li} ch:{ch}')
            try:
                ind = char_list.index(ch)
                print(f'ind:{ind} index')
            except ValueError:
                ind = n_chars - 1
                print(f'ind:{ind} value error')
            tensor[li][0][ind] = 1
        return tensor

    t = title_to_tensor(char_list)
    print(t)
