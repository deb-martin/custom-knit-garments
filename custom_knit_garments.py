import matplotlib
import matplotlib.pyplot as plt
import itertools
import numpy as np
from collections import OrderedDict
from operator import getitem
import textwrap as tr
import fpdf
import math


class Point:
    def __init__(self, x_val, y_val):
        self.x_val = x_val
        self.y_val = y_val
        self.coord = {"x": x_val, "y": y_val}


class Seg:
    def __init__(self, point1, point2):
        self.coord1 = point1.coord
        self.coord2 = point2.coord
        self.seg = [point1.coord, point2.coord]
        self.x_vals = np.array([point1.coord["x"], point2.coord["x"]])
        self.y_vals = np.array([point1.coord["y"], point2.coord["y"]])
        # self.length = d=√((x2 – x1)² + (y2 – y1)²)
        self.length = ((self.x_vals[1] - self.x_vals[0]) ** 2 + (self.y_vals[1] - self.y_vals[0]) ** 2) ** .5
        self.midpoint = Point((self.x_vals[1] + self.x_vals[0]) / 2, (self.y_vals[1] + self.y_vals[0]) / 2)

    def contains_y(self, y_value):
        return not (y_value < min(self.y_vals) or y_value > max(self.y_vals))

    def x_intercept(self, y_value):
        if self.contains_y(y_value):
            if self.y_vals[0] > self.y_vals[1]:
                # need to flip the order of points if y values are descending
                return np.interp(y_value, (self.y_vals[1], self.y_vals[0]), (self.x_vals[1], self.x_vals[0]))
            else:
                return np.interp(y_value, self.y_vals, self.x_vals)
        raise Exception("Module custom_knit_garments: No y intercept found.  "
                        "Must use Seg method contains_y before using Seg method x_intercept.")

    @property
    def all_x_vals(self):  # may not ever use this
        x_intercepts = []
        count = min(self.y_vals)
        while count <= max(self.y_vals):
            x_intercepts.append(self.x_intercept(count))
            count += 1
        return x_intercepts


class Shape:
    """
    class Shape has no init because it is used as a super class solely to define methods for all
    its subclasses. Shape subclasses are used to define all different shape types.
    EXAMPLES are - Body, PatternPiece.
    Since all shapes are created by subclasses of this super class, Shape itself
    needs no constructor.
    The subclasses of Shape use points or something from which points can be derived
    in their respective constructors, therefore, it is safe
    to ignore unresolved point reference warnings for class Shape
    """

    @property
    def y_vals(self):
        y_vals = []
        for point in self.points:
            y_vals.append(point.coord["y"])
        y_vals.append(self.points[0].coord["y"])
        return y_vals

    @property
    def x_vals(self):
        x_vals = []
        for point in self.points:
            x_vals.append(point.coord["x"])
        x_vals.append(self.points[0].coord["x"])
        return x_vals

    @property
    def segments(self):
        segments = [Seg(pair[0], pair[1]) for pair in itertools.pairwise(self.points)]
        # for pair in itertools.pairwise(self.points):
        #     segments.append(Seg(pair[0], pair[1]))
        segments.append(Seg(self.points[-1], self.points[0]))
        return segments


class Body(Shape):
    def __init__(self, body_data, person):
        self.points = []  # Necessary - the ordered list of point tuples which defines the closed shape
        self.person = person
        # sort measurements by height
        # see sort_nested_dict_by_key.py scratch file for example
        # requires from operator import getitem
        sorted_body = OrderedDict(sorted(body_data.items(),
                                         key=lambda x: getitem(x[1], 'height')))

        # create points and make an ordered list of points
        def create_body_point(place, left=True, circumferential=True):
            if left and circumferential:
                point = Point(-sorted_body[place]["meas"] / 4, sorted_body[place]["height"])
                return point
            if not left and circumferential:
                point = Point(sorted_body[place]["meas"] / 4, sorted_body[place]["height"])
                return point
            if left and not circumferential:
                point = Point(-sorted_body[place]["meas"] / 2, sorted_body[place]["height"])
                return point
            if not left and not circumferential:
                point = Point(sorted_body[place]["meas"] / 2, sorted_body[place]["height"])
                return point
            raise Exception("module: points_and_segs create_body_point definition has a problem")

        for place in sorted_body:
            if place != "frontNeck" and place != "backNeck":
                this_point = create_body_point(place, circumferential=sorted_body[place]["circumferential"])
                self.points.append(this_point)
        self.points.append(create_body_point("backNeck"))
        self.points.append(Point(0, y_val=sorted_body["backNeck"]["height"]))
        self.points.append(Point(0, y_val=sorted_body["frontNeck"]["height"]))
        self.points.append(Point(x_val=sorted_body["frontNeck"]["meas"] / 6, y_val=sorted_body["frontNeck"]["height"]))
        for place in sorted_body.__reversed__():
            if place != "frontNeck" and place != "backNeck":
                this_point = create_body_point(place, left=False, circumferential=sorted_body[place]["circumferential"])
                self.points.append(this_point)

    def add_to_subplot(self, subplot):  # sets artists for body plots
        subplot.plot(self.x_vals,
                     self.y_vals,
                     color="grey",
                     label="body")
        subplot.legend()


class PatternPiece(Shape):
    def __init__(self, points):
        self.points = points


class PDF(fpdf.FPDF):
    # page width = 215.9mm
    # column 1 span = 58.6mm
    # column 2 span = 123mm
    # col 1 x pos = 10
    # col 2 x pos = 78.6

    def header(self):
        self.set_font(family="Helvetica", style="", size=12)
        width = self.get_string_width(self.title) + 6
        # self.image("./images/stitches_logo.png", x=((210 - width) / 2) - 5, y=15, w=10, h=10, type='', link='')
        self.set_x((216 - width) / 2)
        self.set_draw_color(255, 204, 239)
        self.set_fill_color(255, 230, 247)
        self.set_text_color(0, 0, 0)
        self.set_line_width(.25)
        if self.page_no() > 1:
            self.cell(
                width,
                10,
                self.title,
                border=0,
                new_x="LMARGIN",
                new_y="NEXT",
                align="C",
                fill=False,
            )
            self.cell(w=80, h=10, new_x="LMARGIN", new_y="NEXT")

    def print_cover_page(self, image, cover_text):
        self.set_font(family="Brazilia", style="", size=36)
        width = self.get_string_width(self.title.upper()) + 6
        self.set_xy((216 - width) / 2, 20)
        self.set_text_color(102, 0, 70)
        self.cell(
            w=width,
            h=10,
            text=self.title.upper(),
            border=0,
            new_x="LMARGIN",
            new_y="NEXT",
            align="C",
            fill=False
        )
        self.image(x=78, y=35, name=image, w=123)
        self.set_font(family="Brazilia", style="", size=12)
        self.set_y(45)
        self.multi_cell(w=59, h=5, text=cover_text, border=0, new_x="LMARGIN", new_y="NEXT", align="L", fill=False)

    def print_stitch_table_page(self, td):
        self.add_page()
        # self.image(x=5+(216/2), y=25, name=image, w=186/2)
        # self.set_font(family="Brazilia", style="", size=14)
        self.set_text_color(102, 0, 70)
        self.set_y(25)
        # self.multi_cell(
        #     w=186/2,
        #     h=6,
        #     text=cover_text,
        #     border=1,
        #     new_x="LMARGIN",
        #     new_y="NEXT",
        #     align="L",
        #     fill=False
        #
        # )
        self.set_font(family="Times", style="", size=10)
        self.set_fill_color(255, 255, 255)
        self.set_text_color(0, 0, 0)
        with self.table(borders_layout='MINIMAL',
                        cell_fill_color=200,
                        cell_fill_mode='ROWS',
                        line_height=self.font_size * 1.5,
                        text_align='CENTER',
                        width=160) as table:
            for data_row in td:
                row = table.row()
                for data in data_row:
                    row.cell(data)

    def print_stitch_map(self, image):
        self.add_page()
        self.image(x=10, y=25, name=image, w=196)

    def footer(self):
        self.set_y(-15)
        self.set_font(family="helvetica", style="I", size=8)
        if self.page_no() != 1:
            self.cell(w=0, h=10, text=f"Page {self.page_no()}/{{nb}}", align="C")

    def chapter_title(self, num, label):
        self.set_font(family="Brazilia", style="", size=24)
        self.set_text_color(0, 0, 0)
        self.set_fill_color(255, 230, 247)
        # self.set_y(-130)
        self.cell(
            w=0,
            h=10,
            text=f"{label}: Knit {num}",
            new_x="LMARGIN",
            new_y="NEXT",
            border="L",
            fill=True,
        )
        self.cell(w=0, h=4)

    def chapter_body(self, file_name):
        # Reading text file:
        with open(file_name, "rb") as fh:
            txt = fh.read().decode("latin-1")
        with self.text_columns(
                ncols=2, gutter=5, text_align="J", line_height=1.5
        ) as cols:
            self.set_font(family="Brazilia", size=12)
            self.set_text_color(0, 0, 0)
            cols.write(txt)
            cols.ln()
            # Final mention in italics:
            # self.set_font(style="I")
            # cols.write(f"end {pattern_piece_name}")

    def print_chapter(self, num, title, file_name):
        self.add_page()
        self.chapter_title(num, title)
        self.chapter_body(file_name)


class Garment:
    """
    All Garment objects are created by subclasses, therefore, Garment needs no init.
    Subclasses of Garment use body and person in their respective inits, therefore, it is safe
    to ignore unresolved body and person reference warnings for class Garment.  All subclasses
    shall have the following:
    a str called person which is the name of the person for whom the garment is designed to fit
    a dict called body which contains the body data
    a tuple called gauge from which is derived:
        a float called spc which is the stitches per centimeter
        a float called rpc which is the rows per centimeter
    a dict called self.pattern_pieces which are uniquely defined by each Garment child to include
        the necessary pattern piece shapes required and referenced by piece names.
    a str called style_name which is the name of the garment style
    a float called hem_length_cm which is the length of the hem in centimeters.
    """

    def set_gauge_for_piece(self, piece, stitches_per_10_cm, rows_per_10_cm):
        self.required_pattern_pieces[piece]['gauge'] = (stitches_per_10_cm, rows_per_10_cm)
        # TODO - figure out how to update everything this affects

    def add_shoulder_extension(self, shoulder_extension_percent):
        # adjust shoulder width using percent distance from outer shoulder to shoulder neck
        self.body_data['shoulderArmhole'] = {key: self.body_data['outerShoulder'][key]
                                             for key in self.body_data['outerShoulder']}
        self.body_data['shoulderArmhole']['meas'] = (((self.body_data['shoulderNeck']['meas'] -
                                                       self.body_data['outerShoulder']['meas']) *
                                                      (shoulder_extension_percent / -100))
                                                     + self.body_data['outerShoulder']['meas'])
        self.body_data['shoulderArmhole']['height'] = (((self.body_data['shoulderNeck']['height'] -
                                                         self.body_data['outerShoulder']['height']) *
                                                        (shoulder_extension_percent / -100))
                                                       + self.body_data['outerShoulder']['height'])

    def add_neck_ease(self, neck_ease_percent):
        # adjust neckline width using percent distance from outer shoulder to shoulder neck
        self.body_data['neckShoulder'] = {key: self.body_data['outerShoulder'][key]
                                          for key in self.body_data['outerShoulder']}
        self.body_data['neckShoulder']['meas'] = (((self.body_data['shoulderNeck']['meas'] -
                                                    self.body_data['outerShoulder']['meas']) *
                                                   ((100 - neck_ease_percent) / 100))
                                                  + self.body_data['outerShoulder']['meas'])
        self.body_data['neckShoulder']['height'] = (((self.body_data['shoulderNeck']['height'] -
                                                      self.body_data['outerShoulder']['height']) *
                                                     ((100 - neck_ease_percent) / 100))
                                                    + self.body_data['outerShoulder']['height'])

    def straighten_neck_shoulder(self, length_cm):
        self.body_data['neckShoulderDrop'] = {key: self.body_data['neckShoulder'][key]
                                              for key in self.body_data['neckShoulder']}
        self.body_data['neckShoulderDrop']['height'] -= length_cm / 2

    def lower_front_neckline(self, percent_to_bust):
        depth = (self.body_data['frontNeck']['height'] - self.body_data['fullBust']['height']) * percent_to_bust / 100
        self.body_data['frontNeck']['height'] -= depth

    def lower_back_neckline(self, depth_cm):
        self.body_data['backNeck']['height'] -= depth_cm

    def lower_underarm(self, depth_cm):
        self.body_data['underArm0']['height'] -= depth_cm
        self.body_data['underArm1']['height'] -= depth_cm
        self.body_data['underArm2']['height'] -= depth_cm

    def straighten_waist(self, length_cm):
        self.body_data['waist1'] = {key: self.body_data['waist'][key] for key in self.body_data['waist']}
        self.body_data['waist2'] = {key: self.body_data['waist'][key] for key in self.body_data['waist']}
        self.body_data['waist1']['height'] -= length_cm / 2
        self.body_data['waist2']['height'] += length_cm / 2

    def add_hem(self, place, straighten_cm):
        self.body_data[place + 'Hem'] = {key: self.body_data[place][key] for key in self.body_data[place]}
        self.body_data[place + 'HemStraighten'] = {key: self.body_data[place][key] for key in self.body_data[place]}
        self.body_data[place + 'Hem']['height'] += self.hem_length_cm
        self.body_data[place + 'HemStraighten']['height'] += (straighten_cm + self.hem_length_cm)

    def create_style_point(self, place, ease, left=True, circumferential=True):
        if left and circumferential:
            point = Point((-self.body_data[place]["meas"] / 4) * (1 + ease / 100), self.body_data[place]["height"])
            return point
        if not left and circumferential:
            point = Point((self.body_data[place]["meas"] / 4) * (1 + ease / 100), self.body_data[place]["height"])
            return point
        if left and not circumferential:
            point = Point((-self.body_data[place]["meas"] / 2) * (1 + ease / 100), self.body_data[place]["height"])
            return point
        if not left and not circumferential:
            point = Point((self.body_data[place]["meas"] / 2) * (1 + ease / 100), self.body_data[place]["height"])
            return point
        raise Exception("class Garment method create_style_point definition has a problem")

    def create_pattern_shape(self, places_with_ease):
        points = []
        for place in places_with_ease:
            points.append(self.create_style_point(place, places_with_ease[place],
                                                  circumferential=self.body_data[place]["circumferential"]))
        for place in reversed(places_with_ease):
            # if place != "hem_length_cm":
            points.append(self.create_style_point(place, places_with_ease[place], left=False,
                                                  circumferential=self.body_data[place]["circumferential"]))
        pattern_piece_shape = PatternPiece(points)
        return pattern_piece_shape

    def create_needle_chart(self, pattern_piece_name):

        def all_stitches(row):
            needle_states = get_needle_states(row)
            sts = [needle for needle in needle_states if needle_states[needle] == "B" or needle_states[needle] == "E"]
            return sts

        def get_needle_states(row):
            # needle_states = {needle: get_needle_status(needle, row) for needle in range(-100, 101) if needle != 0}
            ints = get_segment_intercepts(row)
            needle_states = {}
            for needle in range(-100, 101):
                a = "A"  # out_of_work
                b = "B"  # in_work
                c = "C"  # selected
                e = "E"  # Not really... keeps track of stitches on split sections
                if needle != 0:
                    status = a
                    if ints[0] <= needle <= ints[1]:
                        status = b
                    if len(ints) > 3:
                        if ints[2] <= needle <= ints[3]:
                            status = e
                    needle_states.update({needle: status})
            return needle_states

        def get_segment_intercepts(row):
            y = row * row_height_cm + min(y_vals)
            intercepts = [int(segment.x_intercept(y) / stitch_width_cm) for
                          segment in shape.segments if segment.contains_y(y)]
            segment_intercepts = np.unique(intercepts)
            return segment_intercepts

        def get_row_status(row):
            status = "knit"
            if row == 0:
                status = "cast on"
            if row == total_rows:
                status = "cast off"
            if row == hem_row:
                status = "hem"
            if split_row:
                status = "split"
            return status

        piece = self.required_pattern_pieces[pattern_piece_name]
        shape = self.pattern_shapes[pattern_piece_name]["pattern_shape"]
        gauge = piece["gauge"]
        stitch_width_cm = 10 / gauge[0]
        row_height_cm = 10 / gauge[1]
        hem_row = int(self.hem_length_cm / row_height_cm)
        y_vals = np.array(shape.y_vals)
        total_rows = int((max(y_vals) - min(shape.y_vals)) / row_height_cm)
        split_row = False
        needle_chart = {row: {"row_status": get_row_status(row),
                              "intercepts": get_segment_intercepts(row),
                              "all": all_stitches(row),
                              "needle_states": get_needle_states(row)}
                        for row in range(0, total_rows + 1)
                        }
        return needle_chart

    def write_instructions(self):
        def write_instructions_for_cast_on():
            print("CAST ON USING WASTE YARN:\n"
                  f"Begin with the carriage on the {cp[1]} side. "
                  f"Place needles from position {leftmost_needle} to position {rightmost_needle}, "
                  f"into working position.  Thread the carriage with waste yarn and fasten a "
                  f"clothespin to the yarn end.  Push the carriage {cd[1]}, to cast on  {total_stitches} "
                  f"total needles.  Push the knitted row against the needle bed and slowly knit one "
                  f"more row.  Hang claw weights along the knitting to evenly distribute weight along "
                  f"the knitting.  Knit for a couple of inches with waste yarn.  With the carriage on "
                  f"the {cp[1]} side, break the waste yarn and secure the tail with a clothespin.  "
                  f"Thread the carriage with your main yarn.\n"
                  f"Set the row counter to zero.", file=file_name)

        def write_instructions_for_hem():
            print(f"These {hem_rows} rows form the reverse side of the hem.  Set the row counter to zero.  "
                  f"Knit {row} more rows to form the front side of the hem. "
                  "Pull all working needles forward and remove the claw weights.  Taking care not "
                  f"to drop stitches from the extended needles, rehang the hem by placing the purl "
                  f"bumps from the first row of main yarn stitches on the needles.  You will be short "
                  f"one purl bump.  This is expected and will not cause a problem.  Push the knitting "
                  f"against the needle bed and rehang the claw weights.  \n"
                  f"Loosen the tension and slowly "
                  f"knit 1 row {cd[1]}.  Reset the tension.\n"
                  f"{total_stitches} total stitches.", file=file_name)

        def write_split_row_instructions():
            print(f"Cast off between needles {needles[1]} and {needles[2]}.\n"
                  f"Place needles {needles[2]} through {needles[3]} on hold.", file=file_name)

        def write_change_instructions():
            if leftmost_needle != last_leftmost_needle:  # if there is a change on the left
                if leftmost_needle > last_leftmost_needle:  # if the left is decreasing
                    print(f"\tDecrease {leftmost_needle - last_leftmost_needle} stitch(es) at left edge.",
                          file=file_name)
                else:
                    print(f"\tIncrease {last_leftmost_needle - leftmost_needle} stitch(es) at left edge.",
                          file=file_name)
            if rightmost_needle != last_rightmost_needle:  # if there is a change on the right
                if rightmost_needle < last_rightmost_needle:  # if the right is decreasing
                    print(f"\tDecrease {last_rightmost_needle - rightmost_needle} stitch(es) at right edge.",
                          file=file_name)
                else:
                    print(f"\tIncrease {rightmost_needle - last_rightmost_needle} stitch(es) at right edge.",
                          file=file_name)

        def write_cast_off_instructions():
            print(f"\nCAST OFF REMAINING STITCHES.", file=file_name)

        def write_split_instructions():
            print(f"\n COMPLETE OPPOSITE SIDE:\n"
                  f"Reset counter to {split_counter}, and knit opposite side, reversing "
                  f"left and right instructions.", file=file_name)

        def write_blocking_instructions():
            print(f"\n BLOCKING:\n"
                  f""f"Remove waste yarn.  Machine knitting needs to rest for at least 8 hours before blocking. "
                  f"This is due to the amount of stretch necessary to knit by machine.  "
                  f"Gently stretch your newly knitted fabric from top to bottom to encourage the stitches to relax.  "
                  f"Place on a flat smooth surface like a counter top and let it relax, preferably overnight.  After "
                  f"resting, soak your knitted piece and gently squeeze out excess water.  Never wring your knitting!  "
                  f"Lay flat on a clean towel and gently align to finished dimensions.  When dry, recheck dimensions, "
                  f"using gentle steam if necessary.\n", file=file_name)

        def write_finishing_instructions():
            print(f"\n FINISHING:\n"
                  f"Seam pieces together along sides.  Pick up stitches along neckline and add finishing of choice.  "
                  f"Insert sleeves in the round, or for sleeveless garments, pick up stitches at armhole and add "
                  f"finishing of choice.  ENJOY <3", file=file_name)

            file_name.close()

        def write_row_counter_instructions():
            print(f"KNIT UNTIL ROW COUNTER READS {row}:", file=file_name)

        def write_carriage_instructions():
            print(f"With carriage on the {carriage_position}, move carriage {carriage_direction}, "
                  f"knitting needles from {leftmost_needle} to {rightmost_needle}.\n"
                  f"{total_stitches} total stitches.", file=file_name)

        for pattern_piece_name in self.required_pattern_pieces:
            file_name = open(f"./results/{self.style_name} {pattern_piece_name} for "
                             f"{self.person} at {self.gauge_string}.txt", "w")
            gauge = self.required_pattern_pieces[pattern_piece_name]["gauge"]
            hem_rows = int(self.hem_length_cm * gauge[1] / 10)
            chart = self.style[pattern_piece_name]["needle_chart"]
            cp = ["left", "right"]  # carriage position
            cd = ["from left to right", "from right to left"]  # carriage direction
            last_leftmost_needle = 0
            last_rightmost_needle = 0
            count = 0  # the number of rows with the same amount of stitches
            split = False  # set the default split condition to False
            split_row = False  # set the default split_row condition to False
            split_counter = 0
            for row in chart:  # iterates through each row
                needles = chart[row]["intercepts"]
                status = chart[row]["row_status"]
                leftmost_needle, rightmost_needle = needles[0], needles[1]  # leftmost section of knitting
                total_stitches = rightmost_needle - leftmost_needle
                if status == "cast on":
                    write_instructions_for_cast_on()
                    last_leftmost_needle = leftmost_needle
                    last_rightmost_needle = rightmost_needle
                    self.style[pattern_piece_name]["needle_chart"][row]['row_status'] = 'See Instructions for Cast On'
                if status == "hem":
                    write_row_counter_instructions()
                    write_instructions_for_hem()
                    last_leftmost_needle = leftmost_needle
                    last_rightmost_needle = rightmost_needle
                    self.style[pattern_piece_name]["needle_chart"][row]['row_status'] = "See Hem Instructions"
                if status == "cast off":
                    write_cast_off_instructions()
                    self.style[pattern_piece_name]["needle_chart"][row]['row_status'] = 'See Instructions for Cast Off'
                else:
                    if leftmost_needle == last_leftmost_needle and rightmost_needle == last_rightmost_needle:
                        count += 1  # keep track of how many rows to knit until something changes
                    else:  # once there is a change
                        self.style[pattern_piece_name]["needle_chart"][row]['row_status'] = 'Increase/Decrease'
                        if row % 2 != 0:  # if the row number is odd
                            carriage_position, carriage_direction = cp[0], cd[0]  # the carriage starts on the left
                        else:  # row number is even
                            carriage_position, carriage_direction = cp[1], cd[1]  # and carriage starts on the right
                        write_row_counter_instructions()
                        if len(needles) == 2:
                            split = False
                        if len(needles) > 3 and split is False:  # compare if this is the first row of a split
                            self.style[pattern_piece_name]["needle_chart"][row]['row_status'] = ('See Instructions for '
                                                                                                 'Split/Hold')
                            split_row = True
                            split = True  # if there are more than 2 unique x intercepts there is a split
                        if split_row is True:
                            split_counter = row
                            write_split_row_instructions()
                            split_row = False
                        else:
                            write_change_instructions()
                        write_carriage_instructions()
                        last_leftmost_needle = leftmost_needle
                        last_rightmost_needle = rightmost_needle
                        count = 0
            if split is True:
                write_split_instructions()
        write_blocking_instructions()
        write_finishing_instructions()

    def add_garment_to_subplot(self, subplot, piece):  # sets artists for garment over body plots
        # plt.style.use('./images/garment.mplstyle')
        # if piece == "Front":
        #     line_color = "FC90CE"
        #     line_style = "dashed"
        #     line_width = 1.5
        # if piece == "Back":
        #     line_color = "cyan"
        #     line_style = "dashed"  # '-', '--', '-.', ':', 'None', ' ', '', 'solid', 'dashed', 'dashdot', 'dotted'
        #     line_width = 1.0
        subplot.plot(self.pattern_shapes[piece]["pattern_shape"].x_vals,
                     self.pattern_shapes[piece]["pattern_shape"].y_vals,
                     # scalex=True,
                     # scaley=True,
                     # color=line_color,
                     # linewidth=line_width,
                     # linestyle=line_style,
                     # marker='o',
                     # markersize=1.5,
                     # alpha=0.8,
                     label=piece)
        subplot.legend()

    def make_and_save_plot_svg_files(self):
        for x in range(1, 5):
            plt.style.use("./images/garment.mplstyle")
            fig, ax = plt.subplots()
            ax.set_aspect(1)
            ax.tick_params(axis='x', labelrotation=90)
            ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(10))
            ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(10))
            ax.set_ylabel(f"height in cm\nwaistline at zero")
            ax.set_xlabel(f"width in cm\nbody center at zero")
            if x != 4:  # add body to plots 1 - 3 and set the grid lines
                ax.axis(xmin=-80, xmax=80, ymin=-120, ymax=80)
                ax.xaxis.set_major_locator(matplotlib.ticker.LinearLocator(numticks=9))
                ax.yaxis.set_major_locator(matplotlib.ticker.LinearLocator(11))
                self.body_shape.add_to_subplot(subplot=ax)
            if x == 1:  # add front and back garment to plot 1 and add title
                plt.style.use("./images/garment.mplstyle")
                ax.set_title("Front and Back over Body Map")
                self.add_garment_to_subplot(subplot=ax, piece="Front")
                self.add_garment_to_subplot(subplot=ax, piece="Back")
            if x == 2:  # add garment front to plot 2 and add title
                ax.set_title("Front over Body Map")
                self.add_garment_to_subplot(subplot=ax, piece="Front")
            if x == 3:  # add back to plot 3 and add title
                ax.set_title("Back over Body Map")
                self.add_garment_to_subplot(subplot=ax, piece="Back")
            if x == 4:  # add front and back to plot 4 for the cover. Remove title and axes
                plt.style.use("./images/cover.mplstyle")
                ax.set_title("")
                ax.set_axis_off()
                self.add_garment_to_subplot(subplot=ax, piece="Front")
                self.add_garment_to_subplot(subplot=ax, piece="Back")
            fig.savefig(fname=f"./results/{self.title} plot {x}.svg", format="svg")

    def make_and_save_stitch_maps(self):
        for pattern_piece_name in self.required_pattern_pieces:
            plt.style.use("images/stitchchart.mplstyle")
            x_vals = [x for row in self.style[pattern_piece_name]['needle_chart']
                      for x in self.style[pattern_piece_name]["needle_chart"][row]["all"]]
            y_vals = [row for row in self.style[pattern_piece_name]['needle_chart']
                      for x in self.style[pattern_piece_name]["needle_chart"][row]["all"]]
            gauge = self.required_pattern_pieces[pattern_piece_name]['gauge']
            ratio = gauge[0] / gauge[1]
            fig = matplotlib.figure.Figure(figsize=[8, 10])
            ax = fig.add_subplot(111)
            # fig, ax = plt.subplots(nrows=1, ncols=1, figsize=[8, 10])
            # ax.axis(xmin=-100, xmax=100)
            # ax.axis(ymin=-10, ymax=450)
            # ax.xaxis.set_major_locator(matplotlib.ticker.LinearLocator(21))
            # ax.yaxis.set_major_locator(matplotlib.ticker.LinearLocator(47))
            # ax.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator(5))
            # ax.yaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator(5))
            ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(10))
            ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(10))
            ax.yaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator(5))
            # ax.tick_params(labelsize=8, colors='black')
            ax.tick_params(axis='x', labelrotation=90)
            ax.set_xlabel("machine needles")
            ax.set_ylabel("row number")
            ax.set_aspect(ratio)
            ax.plot(x_vals,
                    y_vals,
                    # marker='^',
                    # markersize=0.5,
                    # alpha=0.5,
                    # mec="hotpink",
                    # mfc="hotpink",
                    # linestyle="",
                    label=pattern_piece_name)
            # ax.legend()
            # ax.grid(visible=True, which='major', color='grey', linestyle='solid', linewidth=1.0)
            ax.grid(visible=True, which='minor', color='#cccccc', linestyle='-', linewidth=1, alpha=0.5)
            ax.set_title(f"{pattern_piece_name} Machine Needle Map by Row")
            fig.savefig(fname=f"./results/stitch_map_{self.style_name}_{pattern_piece_name}_{self.person}"
                              f"_{self.gauge_string}.svg", format="svg")
            if __name__ == "__main__":
                print(f"{self.style_name} {pattern_piece_name} for {self.person} at {self.gauge_string} "
                      f"stitch plot.svg saved to results")

    def create_data_for_stitch_table(self, pattern_piece_name):
        table_data = [["col A", "col B"], ["row 1 col A", "row1 col B"], ["row 2 col A", "row2 col B"]]
        column_names = ["ROW", "STATUS", "NEEDLES IN WORK"]
        nc = self.style[pattern_piece_name]['needle_chart']
        # ints = nc[key]['intercepts']
        table_data = [[f"Row {key}", nc[key]['row_status'], str(nc[key]['intercepts'])]
                      for key in nc.keys() if nc[key]['row_status'] != 'knit']
        table_data.reverse()
        table_data.append(column_names)
        table_data.reverse()
        return table_data

    def create_pdf(self):
        pdf = PDF(orientation='P', format='letter', unit='mm')
        pdf.add_font(family="Brazilia", style="", fname="Brazilia.ttf")
        pdf.set_title(f"{self.style_name} for {self.person}")
        pdf.set_author("Custom Knit Garments")
        pdf.set_margins(10, 15, 10)
        pdf.add_page()
        pdf.print_cover_page(image=f"./results/{self.title} plot 4.svg",
                             cover_text=f"{self.cover_text} yarn estimate: {self.total_yarn_meters} meters.")
        for pattern_piece_name in self.required_pattern_pieces:
            stitch_map = f'./results/stitch_map_{self.style_name}_{pattern_piece_name}_{self.person}_{self.gauge_string}.svg'
            pdf.print_chapter(num=self.required_pattern_pieces[pattern_piece_name]["number_to_make"],
                              title=f"{pattern_piece_name}",
                              file_name=f"./results/{self.style_name} {pattern_piece_name} for {self.person}"
                                        f" at {self.gauge_string}.txt")
            pdf.print_stitch_table_page(td=self.create_data_for_stitch_table(pattern_piece_name=pattern_piece_name))
            pdf.print_stitch_map(image=stitch_map)
        pdf.output(f"./patterns/{self.title}.pdf")

    def create_style(self):
        style = {pattern_piece_name: {
            "pattern_shape": self.pattern_shapes[pattern_piece_name]["pattern_shape"],  # shape obj in cm
            "number_to_make": self.required_pattern_pieces[pattern_piece_name]["number_to_make"],
            "yarn_meters_per_piece": int(0),  # populated with self.calculate_required_yarn_amount_meters(),
            "needle_chart": self.create_needle_chart(pattern_piece_name)
        } for pattern_piece_name in self.required_pattern_pieces}
        return style

    def calculate_required_yarn_amount_meters(self):
        yarn_meters = 0
        for piece in self.required_pattern_pieces:
            # estimate yarn length per stitch using piece gauge
            gauge = self.required_pattern_pieces[piece]['gauge']
            stitch_width = 10 / gauge[0]
            stitch_height = 10 / gauge[1]
            stitch_length_meters = (stitch_width + stitch_height) * 2 / 100
            total_stitches = len([x for row in self.style[piece]['needle_chart']
                                  for x in self.style[piece]["needle_chart"][row]["all"]])
            yarn_length = int(stitch_length_meters * total_stitches)
            self.style[piece]["yarn_meters_per_piece"] = yarn_length
            yarn_meters += yarn_length * self.required_pattern_pieces[piece]["number_to_make"]
        return yarn_meters

    def make_all(self):  # used in init of Garment subclasses
        self.pattern_shapes = {
            key: {"pattern_shape": self.create_pattern_shape(self.required_pattern_pieces[key]["places_with_ease"])}
            for key in self.required_pattern_pieces}
        self.style = self.create_style()
        self.total_yarn_meters = self.calculate_required_yarn_amount_meters()
        # self.make_and_save_plot_canvas()  # this is for multiple plots on one canvas
        self.make_and_save_plot_svg_files()
        self.make_and_save_stitch_maps()
        self.write_instructions()
        self.create_pdf()


class Tshirt(Garment):
    def __init__(self, body_data, person, gauge=(10, 10)):
        '''
        :param body_data: imported from measurement data file
        :param person: imported from measurement data file
        :param gauge: type tuple stitches per 10 cm, rows per 10 cm
        '''
        self.style_name = "T Shirt"
        self.person = person
        self.body_data = body_data
        self.body_shape = Body(body_data, person)
        self.gauge_string = f'gauge {gauge[0]} {gauge[1]}'
        self.title = f'{self.style_name} for {self.person} at {self.gauge_string}'
        self.straighten_waist(5)  # cm
        self.lower_underarm(5)  # cm
        self.add_shoulder_extension(0)  # percent
        self.add_neck_ease(10)  # percent
        self.straighten_neck_shoulder(3)  # cm
        self.lower_front_neckline(percent_to_bust=10)
        self.hem_length_cm = 2
        self.add_hem(place="lowHip", straighten_cm=1)
        front_places_with_ease_percent = {
            "lowHip": -10,
            "lowHipHem": -10,
            "lowHipHemStraighten": -10,
            "waist1": 15,
            "waist2": 15,
            "fullBust": 0,
            # "highBust": 5,  # not needed for boxy shape
            # "underArm1": 15,  # not needed for boxy shape
            # "underArm2": 15,  # not needed for boxy shape
            "shoulderArmhole": 0,
            "neckShoulder": 0,
            "neckShoulderDrop": 0,
            "frontNeck": -20
        }
        back_places_with_ease_percent = {
            "lowHip": 0,
            "lowHipHem": 0,
            "lowHipHemStraighten": 0,
            "waist1": 15,
            "waist2": 15,
            "fullBust": -5,
            # "highBust": 5,  # not needed for boxy shape
            # "underArm1": 15,  # not needed for boxy shape
            # "underArm2": 15,  # not needed for boxy shape
            "shoulderArmhole": 0,
            "neckShoulder": 0,
            "neckShoulderDrop": 0,
        }
        self.required_pattern_pieces = {
            "Front": {"places_with_ease": front_places_with_ease_percent,
                      "number_to_make": int(1),
                      "gauge": gauge},  # uses default but there is a method to change this
            "Back": {"places_with_ease": back_places_with_ease_percent,
                     "number_to_make": int(1),
                     "gauge": gauge}  # uses default but there is a method to change this
        }
        self.cover_text = (f"Custom Fitted Tee\n\n"
                           f"Crew neckline finished with custom edging of choice\n\n"
                           f"Sleeveless Design finished with custom edging of choice\n\n"
                           f"Fitted waist with  {front_places_with_ease_percent['waist1']}% "
                           f"ease at the front waist "
                           f"and {back_places_with_ease_percent['waist1']}% "
                           f"ease at the back waist\n\n"
                           f"Custom Fitted Low Hip Length with {front_places_with_ease_percent['lowHip']} "
                           f"% ease at front low hip and {back_places_with_ease_percent['lowHip']} "
                           f"% ease at back low hip\n\n"
                           f"{self.hem_length_cm} cm self hem\n\n"
                           f"Customized instructions specifically designed for "
                           f"machine gauge of {self.gauge_string}.\n\n")
        self.make_all()


class Dress(Garment):
    def __init__(self, body_data, person, gauge=(10, 10)):
        '''
        :param body_data: imported from measurement data file
        :param person: imported from measurement data file
        :param gauge: type tuple stitches per 10 cm, rows per 10 cm
        '''
        self.style_name = "Dress"
        self.person = person
        self.body_data = body_data
        self.body_shape = Body(body_data, person)
        self.gauge_string = f'gauge {gauge[0]} {gauge[1]}'
        self.title = f'{self.style_name} for {self.person} at {self.gauge_string}'
        self.straighten_waist(5)  # cm
        self.lower_underarm(3)  # cm
        self.add_shoulder_extension(-50)  # percent
        self.add_neck_ease(0)  # percent
        self.straighten_neck_shoulder(3)  # cm
        self.lower_front_neckline(percent_to_bust=110)
        self.hem_length_cm = 2
        self.add_hem(place="belowKnees", straighten_cm=1)
        front_places_with_ease_percent = {
            "belowKnees": 20,
            "belowKneesHem": 20,
            "belowKneesHemStraighten": 20,
            "fullThighs": 2,
            "seatDepth": 2,
            "lowHip": 0,
            # "highHip": -2,
            "waist1": 5,
            "waist2": 5,
            "fullBust": 5,
            "underArm0": 3,
            "underArm1": 5,
            "underArm2": 2,
            "shoulderArmhole": 0,
            "neckShoulder": 0,
            "neckShoulderDrop": 0,
            "frontNeck": -80
        }
        back_places_with_ease_percent = {
            "belowKnees": 20,
            "belowKneesHem": 20,
            "belowKneesHemStraighten": 20,
            "fullThighs": 0,
            "seatDepth": 3,
            "lowHip": 2,
            "highHip": 2,
            "waist1": -3,
            "waist2": -3,
            "fullBust": -10,
            "underArm0": 2,
            "underArm1": 5,
            "underArm2": 0,
            "shoulderArmhole": 0,
            "neckShoulder": 0,
            "neckShoulderDrop": 0
        }
        self.required_pattern_pieces = {
            "Front": {"places_with_ease": front_places_with_ease_percent,
                      "number_to_make": int(1),
                      "gauge": gauge},  # uses default but there is a method to change this
            "Back": {"places_with_ease": back_places_with_ease_percent,
                     "number_to_make": int(1),
                     "gauge": gauge}  # uses default but there is a method to change this
        }
        self.cover_text = (f"Custom Fitted Dress\n\n"
                           f"V neckline finished with edging of choice\n\n"
                           f"Close fitting waist with  {front_places_with_ease_percent['waist1']}% "
                           f"ease at the front waist "
                           f"and {back_places_with_ease_percent['waist1']}% "
                           f"ease at the back waist\n\n"
                           f"Custom Fitted Hip Curve with {front_places_with_ease_percent['highHip']} "
                           f"% ease at front hip and {back_places_with_ease_percent['highHip']} "
                           f"% ease at back hip\n\n"
                           f"Below Knee Length\n\n"
                           f"{self.hem_length_cm} cm self hem\n\n"
                           f"Customized instructions specifically designed for "
                           f"machine gauge of {self.gauge_string}.\n\n")
        self.make_all()


class Pencil_Skirt(Garment):
    def __init__(self, body_data, person, gauge=(10, 10)):
        '''
        :param body_data: imported from measurement data file
        :param person: imported from measurement data file
        :param gauge: type tuple stitches per 10 cm, rows per 10 cm
        '''
        self.style_name = "Pencil Skirt"
        self.person = person
        self.body_data = body_data
        self.body_shape = Body(body_data, person)
        self.gauge_string = f'gauge {gauge[0]} {gauge[1]}'
        self.title = f'{self.style_name} for {self.person} at {self.gauge_string}'
        self.straighten_waist(5)  # cm
        self.hem_length_cm = 2
        self.add_hem(place="belowKnees", straighten_cm=1)
        front_places_with_ease_percent = {
            "belowKnees": 20,
            "belowKneesHem": 20,
            "belowKneesHemStraighten": 20,
            "fullThighs": 2,
            "seatDepth": 2,
            "lowHip": 0,
            "highHip": 0,
            "waist1": 0,
            "waist2": 0
        }
        back_places_with_ease_percent = {
            "belowKnees": 20,
            "belowKneesHem": 20,
            "belowKneesHemStraighten": 20,
            "fullThighs": 0,
            "seatDepth": 3,
            "lowHip": 2,
            "highHip": 2,
            "waist1": -3,
            "waist2": -3
        }
        self.required_pattern_pieces = {
            "Front": {"places_with_ease": front_places_with_ease_percent,
                      "number_to_make": int(1),
                      "gauge": gauge},  # uses default but there is a method to change this
            "Back": {"places_with_ease": back_places_with_ease_percent,
                     "number_to_make": int(1),
                     "gauge": gauge}  # uses default but there is a method to change this
        }
        self.cover_text = (f"Custom Fitted Pencil Skirt\n\n"
                           f"Close fitting waist with  {front_places_with_ease_percent['waist1']}% "
                           f"ease at the front waist "
                           f"and {back_places_with_ease_percent['waist1']}% "
                           f"ease at the back waist\n\n"
                           f"Fold over waist hem allows for optional (recommended) elastic waistband\n\n"
                           f"Custom Fitted Hip Curve with {front_places_with_ease_percent['highHip']} "
                           f"% ease at front hip and {back_places_with_ease_percent['highHip']} "
                           f"% ease at back hip\n\n"
                           f"Below Knee Length\n\n"
                           f"{self.hem_length_cm} cm self hem\n\n"
                           f"Customized instructions specifically designed for "
                           f"machine gauge of {self.gauge_string}.\n\n")
        self.make_all()
