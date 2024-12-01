#!/usr/bin/env python
# coding=utf-8

import torch
import matplotlib.markers as mmarkers
import matplotlib.pyplot as plt

def plot(x, y, c):
  ax = plt.gca()
  sc = ax.scatter(x, y, color='black')
  paths = []
  for i in range(len(x)):
     if c[i].item()== 0:
         marker_obj = mmarkers.MarkerStyle('o')# 圆点标记
     else:
         marker_obj = mmarkers.MarkerStyle('x')# 叉形标记
     path = marker_obj.get_path().transformed(marker_obj.get_transform())
     paths.append(path)
  sc.set_paths(paths)


if __name__ == '__main__':
    n_data = torch.ones(100, 2)
    xy0 = torch.normal(2 * n_data, 1.5)  # 生成均值为2、标准差为1.5的随机数组成的矩阵
    c0 = torch.zeros(100)
    xy1 = torch.normal(-2 * n_data, 1.5)  # 生成均值为−2、标准差为1.5的随机数组成的矩阵
    c1 = torch.ones(100)
    x, y = torch.cat((xy0, xy1), 0).type(torch.FloatTensor).split(1, dim=1)
    x = x.squeeze()
    y = y.squeeze()
    c = torch.cat((c0, c1), 0).type(torch.FloatTensor)

    plot(x, y, c)
    plt.show()

    w = torch.tensor([1., ], requires_grad=True)  # 随机初始化w
    b = torch.zeros((1), requires_grad=True)  # 使用0初始化b
    xx = torch.arange(-4, 5)
    lr = 0.02  # 学习率
    for iteration in range(1000):
        # 前向传播
        loss = ((torch.sigmoid(x * w + b - y) - c) ** 2).mean()
        # 反向传播
        loss.backward()
        # 更新参数
        b.data.sub_(lr * b.grad)  # b = b - lr*b.grad
        w.data.sub_(lr * w.grad)  # w = w - lr*w.grad
        # 绘图
        if iteration % 3 == 0:
            plot(x, y, c)
        yy = w * xx + b
        plt.plot(xx.data.numpy(), yy.data.numpy(), 'r-', lw=5)
        plt.text(-4, 2, 'Loss=%.4f' % loss.data.numpy(), fontdict={'size': 20, 'color': 'black'})
        plt.xlim(-4, 4)
        plt.ylim(-4, 4)
        plt.title("Iteration:{}\nw:{},b:{}".format(iteration, w.data.numpy(), b.data.numpy()))
        plt.show()
        if loss.data.numpy() < 0.03:  # 停止条件
           break