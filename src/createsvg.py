#!/usr/bin/env python3

"""
    Analog Clock Applet for the Budgie Panel
    createSVG - Used to create the SVG file used by Analog Clock Applet

    Copyright © 2020 Samuel Lane
    http://github.com/samlane-ma/

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

class createSVG:

    def __init__(self, filename, size_x=100, size_y=100):
        self.filename = filename
        self.width = str(size_x)
        self.height = str(size_y)
        self.svgitems = []

        self.svgheader = '<?xml version="1.0" encoding="utf-8" ?>'
        self.set_size(size_x, size_y)
        self.svgfooter = '</svg>'

    def clear_svg(self):
        self.svgitems.clear()

    def add_circle(self, cx, cy, r, fill, stroke, stroke_width):
        svgcircle = ('<circle cx="' + str(cx) + '" cy="' + str(cy) + '" fill="'
                     + fill + '" r="' + str(r) + '" stroke="' + stroke
                     + '" stroke-width="' + str(stroke_width) +'" />')
        self.svgitems.append(svgcircle)

    def add_line(self, x_start, y_start, x_end, y_end, stroke, stroke_width):
        svgline = ('<line stroke="' + stroke + '" stroke-width="' + str(stroke_width)
                   + '" x1="' + str(x_start) + '" x2="' + str(x_end) + '" y1="'
                   + str(y_start) + '" y2="' + str(y_end) + '" />')
        self.svgitems.append(svgline)

    def write_svg(self):
        try:
            with open(self.filename, "w") as svgfile:
                svgfile.write(self.svgheader)
                svgfile.write(self.svgsize)
                for line in self.svgitems:
                    svgfile.write(line)
                svgfile.write(self.svgfooter)
        except IOError:
            print("unable to write svg")

    def set_filename(self, filename):
        self.filename = filename

    def set_size(self, x, y):
        self.svgsize =  ('<svg height="'+ str(y) + '" width="' + str(x) + '">')

