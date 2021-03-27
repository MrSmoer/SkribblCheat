# SkribblCheat
A python script that can convert .svg polyline drawings to mouse movement for drawing online Games like Skribbl.io or Garticphone.com
It only works with files that are exclusively made from Polylines. Intendet to be used with https://github.com/LingDong-/linedraw which is able to convert common images into polyline .svg-files

## Usage
You need to import pynput:
```shell
$ pip install pynput
```

Convert an image to line drawing and export .SVG format:

```shell
$ python main.py [-ip [INPUT_PATH]]
```
