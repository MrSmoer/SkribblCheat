# !python3
import os
import re
import sys
import threading
import time
from typing import Type
from xml.dom import minidom

from pynput import keyboard
from pynput import mouse as ms
from pynput.mouse import Button

from linedrawmaster import linedraw
import linedrawmaster.filters

from urllib.request import urlopen

mouse = ms.Controller()
tlc = None
brc = None
brc_available = threading.Event()

biggestY = 0
biggestX = 0

drwblCnvsX = 0
drwblCnvsY = 0


def on_click(x, y, button, pressed):
    if not pressed:
        # Stop listener
        return False


def on_press(key):
    try:
        mouse.release(Button.left)
        os._exit(1)
        print('alphanumeric key {0} pressed'.format(key.char))
        print('adsfadfsa')
    except AttributeError:
        print('special key {0} pressed'.format(
            key))


def initialize():
    print(
        "Please select your programm and then click at the two corners of the canvas (top left and bottom right). Press any key to cancel.")
    with ms.Listener(
            on_click=on_click) as listener:
        listener.join()

    print('Please select, the top left corner of your canvas by clicking.')
    with ms.Listener(
            on_click=on_click) as listener:
        listener.join()

    global tlc
    tlc = mouse.position

    print('Please select, the bottom right corner of your canvas by clicking.')
    with ms.Listener(
            on_click=on_click) as listener:
        listener.join()
    global brc
    brc = mouse.position
    mouse.position = tlc
    print('thread finished')
    brc_available.set()


def getDrawabableCanvasSize(polylines):
    print('Scaling...')
    global biggestX
    global biggestY

    for i in range(len(polylines)):  # goes throug all polylines
        points = hyphen_split(polylines[i])  # Splits polylines to individual points
        for c in range(len(points)):  # goes throug all points on polyline
            cord = points[c].split(',')  # splits points in x and y axis
            if float(cord[0]) > (biggestX - 5):
                biggestX = float(cord[0]) + 5
            if float(cord[1]) > (biggestY - 5):
                biggestY = float(cord[1]) + 5
    # print('TLC: ', tlc)
    # print('bigX: ', biggestX)
    # print('bigY: ', biggestY)

    cnvswidth = tuple(map(lambda i, j: i - j, brc, tlc))[0]
    cnvsheight = tuple(map(lambda i, j: i - j, brc, tlc))[1]
    cnvsapr = cnvswidth / cnvsheight
    # print('Canvasaspr: ', cnvsapr)
    drwblcnvaspr = biggestX / biggestY
    # print('drwnble aspr: ', drwblcnvaspr)

    if drwblcnvaspr < cnvsapr:  # es mus h vertikal saugend
        # print('es mus h vertikal saugend')
        finalheight = cnvsheight
        finalwidth = finalheight * drwblcnvaspr

    else:  # es muss horizontal saugend, oder aspect ratio ist eh gleich
        # print('es muss horizontal saugend, oder aspect ratio ist eh gleich')
        finalwidth = cnvswidth
    scalefactor = finalwidth / biggestX
    # print(scalefactor)
    return scalefactor


def drawLine(line):
    #print(line)
    # print(points)
    beginpoint = line[0]
    mouse.position = beginpoint
    mouse.press(Button.left)
    for c in range(len(line)):  # goes throug all points on polyline
        beginpoint = line[c]
        if len(line) > c + 1:
            destpoint = line[c + 1]
            mouse.position = beginpoint
            time.sleep(0.0001)
            #mouse.press(Button.left)
            # time.sleep(0.01)
            mouse.position = destpoint
            # time.sleep(0.01)
            #mouse.release(Button.left)
        else:
            destpoint = tlc
            # print("finished line")
    mouse.release(Button.left)


def formatPoint(p, scale):
    strcord = p.split(',')
    # print(scale)
    # print(tlc)
    x = float(strcord[0]) * scale + tlc[0]  # + drwblCnvsX/2
    y = float(strcord[1]) * scale + tlc[1]  # + drwblCnvsY/2
    # print('x: ', x)
    # print('y: ', y)
    thistuple = (int(x), int(y))
    return thistuple


def hyphen_split(a):
    return re.findall("[^,]+\,[^,]+", a)
    # ['id|tag1', 'id|tag2', 'id|tag3', 'id|tag4']


def convertLines(polylines, scalefactor):
    convertedLines = []
    for i in range(len(polylines)):
        line = polylines[i]
        points = hyphen_split(line)
        convertedLine =[]
        for c in range(len(points)):
            convertedPoint = formatPoint(points[c], scalefactor)
            convertedLine.append(convertedPoint)
        convertedLines.append(convertedLine)
    return convertedLines


def skribblcheat(polylines):
    listener = keyboard.Listener(
        on_press=on_press)
    listener.start()

    thread = threading.Thread(target=initialize())  # waits for initializing function (two dots)
    thread.start()
    brc_available.wait()

    scalefactor = getDrawabableCanvasSize(polylines)

    print('Drawing...')

    convertedLines = convertLines(polylines, scalefactor)

    for c in range(len(polylines)):
        drawLine(convertedLines[c])
        #print(i/len(polylines)*100)
        # Progress bar
        n=len(polylines)
        j = (c + 1) / n
        sys.stdout.write('\r')
        # the exact output you're looking for:
        sys.stdout.write("[%-20s] %d%%" % ('='*int(20*j), 100*j))
        sys.stdout.flush()

    mouse.release(Button.left)
    sys.stdout.write('\r')
    # the exact output you're looking for:
    sys.stdout.write("Done!                                                  ")
    sys.stdout.flush()


def getlinesfromsvg(loclpath):
    doc = minidom.parse(loclpath)  # parseString also exists
    lcllines = [path.getAttribute('points') for path
                in doc.getElementsByTagName('polyline')]
    doc.unlink()
    return lcllines


if __name__ == '__main__':
    try:
        if sys.argv[1] == '-i':
            try:
                filepath = sys.argv[2]
                print(filepath)
                SVG_R = r'(?:<\?xml\b[^>]*>[^<]*)?(?:<!--.*?-->[^<]*)*(?:<svg|<!DOCTYPE svg)\b'
                SVG_RE = re.compile(SVG_R, re.DOTALL)

                with open(filepath, 'r') as f:
                    is_svg = False
                    file_contents = f.read()  # .decode('latin_1')  # avoid any conversion exception
                    is_svg = SVG_RE.match(file_contents) is not None
                    print(is_svg)
            except Exception as e:
                print(e)

            if not is_svg:
                lines = 'test'
                print('imhere')
                print(filepath)
                linedraw.sketch(filepath)
                lines = getlinesfromsvg('linedrawmaster/output/out.svg')
                # print(lines)
                print('Conversion done!')
            else:
                lines = getlinesfromsvg(filepath)
    except Exception as e:
        print('Somethings incorrect1')
        print(e)
    # print(lines)
    skribblcheat(lines)

# google url                     |query | image
# https://www.google.com/search?q=banane&tbm=isch
