#!/usr/bin/env python
# coding=utf-8
import copy


def f1():
    l1 = [1]
    l2 = [10]
    l3 = [100]

    l = [l1, l2, l3]
    l[0].append(2)
    print(l)
    print(l1)

    ll = l
    l[0].append(3)
    print(l)
    print(ll)
    print(l1)

    lll = copy.deepcopy(l)
    lll[0].append(3)
    print(l)
    print(ll)
    print(lll)
    print(l1)

def f2(bar=[]):
    bar.append(1)
    return bar

if __name__ == '__main__':
    f1()

    print(f2())
    print(f2())
