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

from argparse import ArgumentParser

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

# ARGS
parser = ArgumentParser()
parser.add_argument('-p', '--path', dest='imagepath', help='Path of the Image to draw', default=None)

args = parser.parse_args()


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
        "Please select your programm and then click at the two corners of the canvas (top left and bottom right). "
        "Press any key to cancel.")
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


def calc_scalefactor(polylines):
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


def draw_line(points):
    # print(line)
    # print(points)
    beginpoint = points[0]
    mouse.position = beginpoint
    mouse.press(Button.left)
    for c in range(len(points)):  # goes throug all points on polyline
        beginpoint = points[c]
        if len(points) > c + 1:
            destpoint = points[c + 1]
            mouse.position = beginpoint
            time.sleep(0.0001)
            mouse.position = destpoint
        # else:
            # print("finished line")
    mouse.release(Button.left)


def format_point(p, scale):
    strcord = p.split(',')
    # print(scale)
    # print(tlc)
    x = float(strcord[0]) * scale + tlc[0]  # + drwblCnvsX/2
    y = float(strcord[1]) * scale + tlc[1]  # + drwblCnvsY/2
    # print('x: ', x)
    # print('y: ', y)
    this_tuple = (int(x), int(y))
    return this_tuple


def hyphen_split(a):
    return re.findall("[^,]+\,[^,]+", a)
    # ['id|tag1', 'id|tag2', 'id|tag3', 'id|tag4']


def convert_lines(polylines, scalefactor):
    converted_lines = []
    for i in range(len(polylines)):
        line = polylines[i]
        points = hyphen_split(line)
        converted_line = []
        for c in range(len(points)):
            converted_point = format_point(points[c], scalefactor)
            converted_line.append(converted_point)
        converted_lines.append(converted_line)
    return converted_lines


def scale_and_convert(polylines):
    scalefactor = calc_scalefactor(polylines)
    converted_lines = convert_lines(polylines, scalefactor)
    return converted_lines

def get_lines_from_svg(loclpath):
    doc = minidom.parse(loclpath)  # parseString also exists
    lcllines = [path.getAttribute('points') for path
                in doc.getElementsByTagName('polyline')]
    doc.unlink()
    return lcllines


def check_is_svg(filepath):
    try:
        svg_r = r'(?:<\?xml\b[^>]*>[^<]*)?(?:<!--.*?-->[^<]*)*(?:<svg|<!DOCTYPE svg)\b'
        svg_re = re.compile(svg_r, re.DOTALL)

        with open(filepath, 'r') as f:
            is_svg = False
            file_contents = f.read()  # .decode('latin_1')  # avoid any conversion exception
            is_svg = svg_re.match(file_contents) is not None
            print(is_svg)
    except Exception as e:
        print(e)
    return is_svg


def get_lines_from_file():
    if args.imagepath is not None:
        global lines
        filepath = args.imagepath
        is_svg = check_is_svg(filepath)
        if is_svg:
            lines = get_lines_from_svg(filepath)
        else:
            lines = None
            print('imhere')
            print(filepath)
            linedraw.sketch(filepath)
            lines = get_lines_from_svg('linedrawmaster/output/out.svg')
            # print(lines)
            print('Conversion done!')
    else:
        print('You should specify an image with "-p [imagepath]"')
    return lines


if __name__ == '__main__':
    lines = get_lines_from_file()

    listener = keyboard.Listener(
        on_press=on_press)
    listener.start()

    thread = threading.Thread(target=initialize())  # waits for initializing function (two dots)
    thread.start()
    brc_available.wait()

    print('Scaling...')
    converted_lines = scale_and_convert(lines)

    print('Drawing...')
    for c in range(len(lines)):
        draw_line(converted_lines[c])
        # print(i/len(polylines)*100)
        # Progress bar
        n = len(lines)
        j = (c + 1) / n
        sys.stdout.write('\r')
        # the exact output you're looking for:
        sys.stdout.write("[%-20s] %d%%" % ('=' * int(20 * j), 100 * j))
        sys.stdout.flush()

    mouse.release(Button.left)
    sys.stdout.write('\r')
    # the exact output you're looking for:
    sys.stdout.write("Done!                                                  ")
    sys.stdout.flush()

# google url                     |query | image
# https://www.google.com/search?q=banane&tbm=isch
