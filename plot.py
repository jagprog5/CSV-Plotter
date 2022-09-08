#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import numpy, sys, time, os
import argparse
from matplotlib import pyplot

def draw(fig, rows, TIME, COLUMN_LABELS, keys):
    fig.clf()

    for i in range(len(rows)):
        if TIME and i == 0:
            continue  # skip the time column

        if TIME:
            pyplot.plot(rows[0], rows[i],
                        label=COLUMN_LABELS[str(keys[i - 1])])
        else:
            pyplot.plot(rows[i], label=COLUMN_LABELS[str(keys[i])])
        fig.canvas.manager.set_window_title('')
        pyplot.legend(loc='best')
    pyplot.xlabel('time (sec)' if TIME else 'frame #')

def on_close(event):
    exit() # on preview close, don't keep re-opening plots

if __name__ == "__main__":
    # ensure that the program producing output is actually flushing the data! This is a gotchya if python is the source
    parser = argparse.ArgumentParser(
        description="csv plotting utility. Pipe csv to stdin. Produces columnwise plots and screenshots.")
    parser.add_argument(
        "labels", help="yaml string which describes what columns to display. e.g. \"{'0': 'position_x'}\"")
    parser.add_argument(
        "-s", "--screenshot-path", help="If not specified, the plots are instead shown on the screen. e.g. -s \"$PWD/img.png\"")
    parser.add_argument(
        "-t", "--time", type=bool, nargs='?', const=True, help="Is the first column the time column? Not specified = false. If true, the column label numbering is: TIME,0,1,2,3,4...")
    parser.add_argument(
        "-p", "--preview", type=float, default=0, help="Roughly every n seconds, display the graph.")
    args = parser.parse_args()
    SCREENSHOT_PATH = args.screenshot_path
    COLUMN_LABELS = yaml.safe_load(args.labels)
    TIME = args.time
    PREVIEW = args.preview
    last_preview_display_time = 0
    del args

    style = os.environ.get("MPL_STYLE")
    if style:
        pyplot.style.use(style)

    keys = COLUMN_LABELS.keys()
    keys = [int(k) for k in keys]

    fig = pyplot.figure()
    fig.canvas.mpl_connect('close_event', on_close)

    rows = [] # init
    for i in range(len(keys) + (1 if TIME else 0)):
        rows.append(numpy.ndarray(dtype=numpy.float32, shape=0))
    insertion_index = 0

    for line in sys.stdin:
        if (insertion_index >= rows[0].shape[0]):
            # dynamic resize rows by doubling
            for i in range(len(rows)):
                rows[i] = numpy.resize(rows[i], (insertion_index * 2 + 1))

        cells = line.split(',')
        if TIME:
            rows[0][insertion_index] = cells[0]
        row_index = 0
        for cell_index in keys:
            rows[row_index + (1 if TIME else 0)][insertion_index] = cells[cell_index + (1 if TIME else 0)]
            row_index += 1

        if PREVIEW != 0 and time.time() - last_preview_display_time > PREVIEW:
            last_preview_display_time = time.time()
            temp_rows = []
            for r in rows:
                temp_rows.append(r[:insertion_index]) # this creates a view, not a copy
            draw(fig, temp_rows, TIME, COLUMN_LABELS, keys)
            pyplot.pause(0.00000001)

        insertion_index += 1
    
    # discard the chaff ˢᵃᶦᵈ ᵐᵒʳᵈᵉᵏᵃᶦˢᵉʳ
    temp_rows = []
    for r in rows:
        temp_rows.append(r[:insertion_index]) # view not copy

    draw(fig, temp_rows, TIME, COLUMN_LABELS, keys)
    if SCREENSHOT_PATH != None:
        fig.savefig(SCREENSHOT_PATH)
    else:
        pyplot.show()