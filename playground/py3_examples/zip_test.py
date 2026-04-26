#!/usr/bin/env python
# coding=utf-8


import zipfile

def get_unzipped_size(zip_path):
    total = 0
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            total += info.file_size   # 解压后的大小
    return total

print(get_unzipped_size("/Users/yingz/Downloads/zbsm.zip"))


import zipfile
import shutil

MAX_SIZE = 1 * 1024**3  # 1GB
written = 0

try:
    with zipfile.ZipFile("/Users/yingz/Downloads/zbsm.zip") as z:
        for info in z.infolist():
            with z.open(info) as src:
                with open(info.filename, "wb") as dst:
                    print(f"Extracting {info.filename}")
                    while True:
                        chunk = src.read(1024 * 1024)
                        if not chunk:
                            break
                        written += len(chunk)
                        if written > MAX_SIZE:
                            raise RuntimeError("zip exceeds max size")
                        dst.write(chunk)
except zipfile.BadZipFile as e:
    # 直接拒绝
    raise ValueError("Invalid or malicious zip file") from e

