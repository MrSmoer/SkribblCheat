
# SkribblCheat
A python3 script that can convert .svg polyline drawings to mouse movement for drawing online Games like Skribbl.io or Garticphone.com
It only works with files that are exclusively made from Polylines. Intendet to be used with https://github.com/LingDong-/linedraw which is able to convert common image formats into polyline .svg-files.

<img src="samples/sample%20banana.jpg" alt="Sample Banana photograph" width="300"><img src="samples/sample%20banana.svg#thumbnail" alt="samples/Sample Banana ScalableVectorGraphics Sketch" width="300"><img src="sample%20banana%20paint.png" alt="Sample Banana drawn in paint" width="300">

## Usage
You need the pynput module:
```shell
$ pip install pynput
```
Open your e.g. Paint before you start the Script, select smallest tool (preferably a pen) for best result.

Press any key to kill the Program.

Start Script from Terminal:
```shell
$ python SkribblCheat.py -i [INPUT_PATH]
```


Click at your Program to focus it and mark the **top left corner** of the area you want the script to draw in and then mark the **bottom right corner**. It will automatically fit your .svg into this area and should start to draw. 
