#!/usr/bin/env python
# coding=utf-8
from constants import DOUBAO_SEED_1_6_THINKING, IMAGE_MODEL_ID
from misc import getArkClient

client = getArkClient()


def chat_demo():
  response = client.chat.completions.create(
    # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
    model=DOUBAO_SEED_1_6_THINKING,
    response_format={"type": "json_object"},
    messages=[
      {"role": "system", "content": "您是一个帮助用户了解鲜花信息的智能助手，并能够输出JSON格式的内容。"},
      {"role": "user", "content": "生日送什么花最好？"},
      {"role": "assistant", "content": "玫瑰花是生日礼物的热门选择。"},
      {"role": "user", "content": "从北京西城区送到东城区"}
    ],
  )
  print(response)
  print(response.choices[0])

def image_demo():
  # 导入OpenAI库
  from openai import OpenAI
  # 加载环境变量
  from dotenv import load_dotenv
  load_dotenv()

  # 请求DALL·E 3生成图片
  response = client.images.generate(
    model=IMAGE_MODEL_ID,
    prompt="画一幅图，图里有欢乐的小松鼠、喝着可乐、海豚正跃出水面，树上倒挂着一只蜘蛛",
    size="1024x1024",
    # quality="standard",
    # n=1,
  )
  print(response)
  # 获取图片URL
  image_url = response.data[0].url
  # 读取图片
  import requests
  image = requests.get(image_url).content
  image_path = "/tmp/generated_image.png"
  with open(image_path, "wb") as f:
    f.write(image)
  print(f"图片已保存到: {image_path}")

# chat_demo()

image_demo()