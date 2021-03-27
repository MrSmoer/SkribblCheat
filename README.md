
# SkribblCheat
A python3 script that can convert(draw) .svg polyline drawings to mouse movement for drawing online Games like Skribbl.io or Garticphone.com
Internally it uses linedraw from LingDong https://github.com/LingDong-/linedraw which is able to convert common image formats into polyline .svg-files that can be drawn.

<img src="samples/banner banana.png">

## Usage
You need the pynput module:
```shell
$ pip install pynput
```
Open your e.g. Paint before you start the Script, select smallest tool (preferably a pen) for best result.

Press any key to kill the Program.

Start Script from Terminal:
```shell
$ python skribblcheat.py -i [INPUT_PATH]
```


Click at your Program to focus it and mark the **top left corner** of the area you want the script to draw in and then mark the **bottom right corner**. It will automatically fit your .svg into this area and should start to draw. 
