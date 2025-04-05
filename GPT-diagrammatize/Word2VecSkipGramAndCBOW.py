#!/usr/bin/env python
# coding=utf-8


# 第一步 构建实验语料库
# 定义一个句子列表，后面会用这些句子来训练CBOW和Skip-Gram模型
sentences = ["Kage is Teacher", "Mazong is Boss", "Niuzong is Boss",
             "Xiaobing is Student", "Xiaoxue is Student",]
# 将所有句子连接在一起，然后用空格分隔成多个单词
words = '  '.join(sentences).split()
# 构建词汇表，去除重复的词
word_list = list(set(words))
# 创建一个字典，将每个词映射到一个唯一的索引
word_to_idx = {word: idx for idx, word in enumerate(word_list)}
# 创建一个字典，将每个索引映射到对应的词
idx_to_word = {idx: word for idx, word in enumerate(word_list)}
voc_size = len(word_list) # 计算词汇表的大小
print("词汇表：", word_list) # 输出词汇表
print("词汇到索引的字典：", word_to_idx) # 输出词汇到索引的字典
print("索引到词汇的字典：", idx_to_word) # 输出索引到词汇的字典
print("词汇表大小：", voc_size) # 输出词汇表大小

# 第二步 生成 Skip-Gram 数据
# 生成Skip-Gram训练数据
def create_skipgram_dataset(sentences, window_size=2):
    data = [] # 初始化数据
    for sentence in sentences: # 遍历句子
        sentence = sentence.split()  # 将句子分割成单词列表
        for idx, word in enumerate(sentence):  # 遍历单词及其索引
            # 获取相邻的单词，将当前单词前后各N个单词作为相邻单词
            for neighbor in sentence[max(idx - window_size, 0):
            min(idx + window_size + 1, len(sentence))]:
                if neighbor != word:  # 排除当前单词本身
                    # 将相邻单词与当前单词作为一组训练数据
                    data.append((word, neighbor))
    return data
# 使用函数创建Skip-Gram训练数据
skipgram_data = create_skipgram_dataset(sentences)
# 打印未编码的Skip-Gram数据样例(前3个)
print("Skip-Gram数据样例(未编码)：", skipgram_data[:3])

# 第三步 进行 One-Hot 编码
# 定义One-Hot编码函数
import torch # 导入torch库
def one_hot_encoding(word, word_to_idx):
    tensor = torch.zeros(len(word_to_idx)) # 创建一个长度与词汇表相同的全0张量
    tensor[word_to_idx[word]] = 1  # 将对应词索引位置上的值设为1
    return tensor  # 返回生成的One-Hot编码后的向量
# 展示One-Hot编码前后的数据
word_example = "Teacher"
print("One-Hot编码前的单词：", word_example)
print("One-Hot编码后的向量：", one_hot_encoding(word_example, word_to_idx))
# 展示编码后的Skip-Gram训练数据样例
# 这里改了原有代码，我理解 target 是目标词，context 是周围的词汇
print("Skip-Gram 数据样例(已编码)：", [(one_hot_encoding(context, word_to_idx), word_to_idx[target])  for target, context in skipgram_data[:3]])

# 定义Skip-Gram类
import torch.nn as nn # 导入neural network
class SkipGram(nn.Module):
    def __init__(self, voc_size, embedding_size):
        super(SkipGram, self).__init__()
        # 从词汇表大小到嵌入层大小(维度)的线性层(权重矩阵)
        self.input_to_hidden = nn.Linear(voc_size, embedding_size, bias=False)
        # 从嵌入层大小(维度)到词汇表大小的线性层(权重矩阵)
        self.hidden_to_output = nn.Linear(embedding_size, voc_size, bias=False)
    def forward(self, X): # 前向传播的方式，X形状为(batch_size, voc_size)
        # 通过隐藏层，hidden形状为 (batch_size, embedding_size)
        hidden = self.input_to_hidden(X)
        # 通过输出层，output_layer形状为 (batch_size, voc_size)
        output = self.hidden_to_output(hidden)
        return output
embedding_size = 2 # 设定嵌入层的大小，这里选择2是为了方便展示
skipgram_model = SkipGram(voc_size, embedding_size)  # 实例化Skip-Gram模型
print("Skip-Gram类：", skipgram_model)

# 训练Skip-Gram类
learning_rate = 0.001 # 设置学习速率
epochs = 5500 # 设置训练轮次
criterion = nn.CrossEntropyLoss()  # 定义交叉熵损失函数
import torch.optim as optim # 导入随机梯度下降优化器
optimizer = optim.SGD(skipgram_model.parameters(), lr=learning_rate)
# 开始训练循环
loss_values = []  # 用于存储每轮的平均损失值
for epoch in range(epochs):
    loss_sum = 0 # 初始化损失值
    for center_word, context in skipgram_data:
        X = one_hot_encoding(center_word, word_to_idx).float().unsqueeze(0) # 将中心词转换为 One-Hot 向量
        y_true = torch.tensor([word_to_idx[context]], dtype=torch.long) # 将周围词转换为索引值
        y_pred = skipgram_model(X)  # 计算预测值
        loss = criterion(y_pred, y_true)  # 计算损失
        loss_sum += loss.item() # 累积损失
        optimizer.zero_grad()  # 清空梯度
        loss.backward()  # 反向传播
        optimizer.step()  # 更新参数
    if (epoch+1) % 100 == 0: # 输出每100轮的损失，并记录损失
        print(f"Epoch: {epoch+1}, Loss: {loss_sum/len(skipgram_data)}")
        loss_values.append(loss_sum / len(skipgram_data))
# 绘制训练损失曲线
import matplotlib.pyplot as plt # 导入matplotlib
# 绘制二维词向量图
plt.rcParams["font.family"]=['SimHei'] # 用来设定字体样式
plt.rcParams['font.sans-serif']=['SimHei'] # 用来设定无衬线字体样式
plt.rcParams['axes.unicode_minus']=False # 用来正常显示负号
plt.plot(range(1, epochs//100 + 1), loss_values) # 绘图
plt.title('训练损失曲线') # 图题
plt.xlabel('轮次') # X轴Label
plt.ylabel('损失') # Y轴Label
plt.show() # 显示图

# 输出Skip-Gram习得的词嵌入
print("Skip-Gram词嵌入：")
for word, idx in word_to_idx.items(): # 输出每个词的嵌入向量
    print(f"{word}: {skipgram_model.input_to_hidden.weight[:,idx].detach().numpy()}")

fig, ax = plt.subplots()
for word, idx in word_to_idx.items():
    # 获取每个单词的嵌入向量
    vec = skipgram_model.input_to_hidden.weight[:,idx].detach().numpy()
    ax.scatter(vec[0], vec[1]) # 在图中绘制嵌入向量的点
    ax.annotate(word, (vec[0], vec[1]), fontsize=12) # 点旁添加单词标签
plt.title('二维词嵌入') # 图题
plt.xlabel('向量维度1') # X轴Label
plt.ylabel('向量维度2') # Y轴Label
plt.show() # 显示图

# 生成CBOW训练数据
def create_cbow_dataset(sentences, window_size=2):
    data = []# 初始化数据
    for sentence in sentences:
        sentence = sentence.split()  # 将句子分割成单词列表
        for idx, word in enumerate(sentence):  # 遍历单词及其索引
            # 获取上下文词汇，将当前单词前后各window_size个单词作为周围词
            context_words = sentence[max(idx - window_size, 0):idx] \
                + sentence[idx + 1:min(idx + window_size + 1, len(sentence))]
            # 将当前单词与上下文词汇作为一组训练数据
            data.append((word, context_words))
    return data

# 使用函数创建CBOW训练数据
cbow_data = create_cbow_dataset(sentences)
# 打印未编码的CBOW数据样例（前三个）
print("CBOW数据样例（未编码）：", cbow_data[:3])

# 定义CBOW模型
import torch.nn as nn # 导入neural network
class CBOW(nn.Module):
    def __init__(self, voc_size, embedding_size):
        super(CBOW, self).__init__()
        # 从词汇表大小到嵌入大小的线性层（权重矩阵）
        self.input_to_hidden = nn.Linear(voc_size,
                                         embedding_size, bias=False)
        # 从嵌入大小到词汇表大小的线性层（权重矩阵）
        self.hidden_to_output = nn.Linear(embedding_size,
                                          voc_size, bias=False)

    def forward(self, X): # X: [num_context_words, voc_size]
        # 生成嵌入：[num_context_words, embedding_size]
        embeddings = self.input_to_hidden(X)
        # 计算隐藏层，求嵌入的均值：[embedding_size]
        hidden_layer = torch.mean(embeddings, dim=0)
        # 生成输出层：[1, voc_size]
        output_layer = self.hidden_to_output(hidden_layer.unsqueeze(0))
        return output_layer
embedding_size = 2 # 设定嵌入层的大小，这里选择2是为了方便展示
cbow_model = CBOW(voc_size,embedding_size)  # 实例化CBOW模型
print("CBOW模型：", cbow_model)

for target, context_words in cbow_data:
    # 将上下文词转换为One-Hot编码后的向量并堆叠
    X = torch.stack([one_hot_encoding(word, word_to_idx) for word in context_words]).float()
    # 将目标词转换为索引值
    y_true = torch.tensor([word_to_idx[target]], dtype=torch.long)

# 定义Skip-Gram模型
import torch.nn as nn # 导入neural network
class SkipGram(nn.Module):
    def __init__(self, voc_size, embedding_size):
        super(SkipGram, self).__init__()
        # 从词汇表大小到嵌入大小的嵌入层（权重矩阵）
        self.input_to_hidden = nn.Embedding(voc_size, embedding_size)
        # 从嵌入大小到词汇表大小的线性层（权重矩阵）
        self.hidden_to_output = nn.Linear(embedding_size, voc_size, bias=False)
    def forward(self, X):
        hidden_layer = self.input_to_hidden(X)  # 生成隐藏层：[batch_size, embedding_size]
        output_layer = self.hidden_to_output(hidden_layer)  # 生成输出层：[batch_size, voc_size]
        return output_layer

X = torch.tensor([word_to_idx[target]], dtype=torch.long)  # 输入是中心词
y_true = torch.tensor([word_to_idx[context]], dtype=torch.long)  # 目标词是周围词