#!/usr/bin/env python

"""
很简陋的一个颜色替换工具，当原图片有背景色的时候请使用这个将背景颜色清除。

运行需要Pillow，如果没有安装的话请输入以下指令安装：
    $ pip install Pillow

输入颜色的时候请在每个值中间加一个空格。
常用的背景颜色有：
- 238 238 238 255
- 241 241 241 255

输入的颜色最终会被替换为透明，输出文件为'noBG.png'。
"""

from PIL import Image
from os.path import splitext

file_name = input("Filename: ")
r, g, b, a = map(int, input("Color(R G B A): ").split())

if not (0 <= r <= 255 or 0 <= g <= 255 or 0 <= b <= 255 or 0 <= a <= 255):
    print("Color value error, please input valid numbers(Range: 0-255).")
    exit(1)

img = Image.open(file_name)
img = img.convert('RGBA')
pixel = img.load()

for x in range(0, img.size[0]):
    for y in range(0, img.size[1]):
        if pixel[x, y] == (r, g, b, 255):
            img.putpixel((x, y), (0, 0, 0, 0))

img.save(splitext(file_name)[0] + '_noBG.png')
