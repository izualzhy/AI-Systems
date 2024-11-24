#!/usr/bin/env python
# coding=utf-8

import spacy

# pip3.12 install -U pip setuptools wheel
# pip3.12 install -U spacy
# python3.12 -m spacy download zh_core_web_sm
if __name__ == '__main__':
   nlp = spacy.load("zh_core_web_sm")
   text =(
   """我家的后面有一个很大的园，相传叫作百草园。现在是早已并屋子一起卖给朱文公的子孙了，连那最末次的相见
   也已经隔了七八年，其中似乎确凿只有一些野草；但那时却是我的乐园。
   不必说碧绿的菜畦，光滑的石井栏，高大的皂荚树，紫红的桑椹；也不必说鸣蝉在树叶里长吟，肥胖的黄蜂伏在菜花
   上，轻捷的叫天子（云雀）忽然从草间直窜向云霄里去了。单是周围的短短的泥墙根一带，就有无限趣味。油蛉在这
   里低唱，蟋蟀们在这里弹琴。翻开断砖来，有时会遇见蜈蚣；还有斑蝥，倘若用手指按住它的脊梁，便会拍的一声，
   从后窍喷出一阵烟雾。何首乌藤和木莲藤缠络着，木莲有莲房一般的果实，何首乌有拥肿的根。有人说，何首乌根是
   有象人形的，吃了便可以成仙，我于是常常拔它起来，牵连不断地拔起来，也曾因此弄坏了泥墙，却从来没有见过有
   一块根象人样。如果不怕刺，还可以摘到覆盆子，象小珊瑚珠攒成的小球，又酸又甜，色味都比桑椹要好得远。
   长的草里是不去的，因为相传这园里有一条很大的赤练蛇。
   """)
   doc = nlp(text)
   print("动词:", [token.lemma_ for token in doc if token.pos_ == "VERB"])
   for entity in doc.ents:
      print(entity.text, entity.label_)
