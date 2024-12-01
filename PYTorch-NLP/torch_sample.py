#!/usr/bin/env python
# coding=utf-8

import torch

if __name__ == '__main__':
    t = torch.tensor([[1, 2, 3], [4, 5, 6]])
    print(t, t.shape, t.dtype)
    print(t.numpy())
    print(t.tolist())

    rand_tensor = torch.rand((3, 3))
    ones_tensor = torch.ones((2, 2))
    zeros_tensor = torch.zeros((2, 3))
    print(rand_tensor)
    print(ones_tensor)
    print(zeros_tensor)

    t1 = torch.tensor([1, 2, 3])
    t2 = torch.tensor([4, 5, 6])
    t3 = torch.cat([t1, t2])
    print(t3)

    t1 = torch.tensor([[1, 2, 3], [1, 2, 3]])
    t2 = torch.tensor([[4, 5, 6], [4, 5, 6]])
    t3 = torch.cat([t1, t2])
    t4 = torch.cat([t1, t2], dim=1)
    print(t3)
    print(t4)

    t1 = torch.tensor([1, 2, 3])
    t2 = torch.tensor([4, 5, 6])
    t3 = torch.stack([t1, t2])
    print(t3)
    print(torch.cat([t1, t2]))

    x = torch.tensor([
        [[0.5, 0.1, 0.3]],
        [[0.8, 0.2, 0.1]]
    ])
    print(x.shape)
    print(x)
    y = x.expand(2, 8, 3)
    print(y.shape)
    print(y)
