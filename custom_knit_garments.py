# import matplotlib
# import matplotlib.pyplot as plt
import itertools
import numpy as np
from collections import OrderedDict
from operator import getitem
import textwrap as tr


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
    def all_x_vals(self):   # may not ever use this
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
    EXAMPLES are - Body, PatternPiece, and Garment.  Garment shapes also have no constructor
    because they have their own subclasses which are used to define different garment shape types.
    Since all shapes are created by child or grandchild classes of this super class, Shape itself
    needs no constructor.
    The subclasses of Shape use points in their respective constructors, therefore, it is safe
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
        segments = []
        for pair in itertools.pairwise(self.points):
            segments.append(Seg(pair[0], pair[1]))
        segments.append(Seg(self.points[-1], self.points[0]))
        return segments


class Body(Shape):
    def __init__(self, body_data, person):
        self.person = person
        # sort measurements by height
        # see sort_nested_dict_by_key.py scratch file for example
        # requires from operator import getitem
        sorted_body = OrderedDict(sorted(body_data.items(),
                                         key=lambda x: getitem(x[1], 'height')))
        # create points and make an ordered list of points
        self.points = []  # this will be an ordered list of point tuples

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
            pass

        self.points.append(create_body_point("backNeck"))
        self.points.append(Point(0, y_val=sorted_body["backNeck"]["height"]))
        self.points.append(Point(0, y_val=sorted_body["frontNeck"]["height"]))
        self.points.append(Point(x_val=sorted_body["frontNeck"]["meas"] / 6, y_val=sorted_body["frontNeck"]["height"]))
        for place in sorted_body.__reversed__():
            if place != "frontNeck" and place != "backNeck":
                this_point = create_body_point(place, left=False, circumferential=sorted_body[place]["circumferential"])
                self.points.append(this_point)
            pass

    def add_to_subplot(self, subplot):  # sets artists for body plots
        subplot.plot(self.x_vals,
                     self.y_vals,
                     color="grey",
                     linewidth=1.0,
                     marker=".",
                     markersize=1.5,
                     alpha=1.0,
                     label="body")
        subplot.legend()
        subplot.grid(visible=True, which='both', color='grey', linestyle='-.', linewidth=0.35)
        subplot.set_title("Garment for " + self.person)


class Garment(Shape):
    """
    class Garment has no init because it is used as a super class solely to define methods
    for all its subclasses. Garment subclasses are used to define all the different styles.
    EXAMPLES are Tshirt, Dress, and Cardigan
    All Garment Shapes are created by subclasses, therefore, Garment needs no constructor.
    Subclasses of Garment use body and person in their respective constructors, therefore, it is safe
    to ignore unresolved body and person reference warnings for class Garment.  All subclasses
    shall have the following:
    a str called person which is the name of the person for whom the garment is designed to fit
    a dict called body which contains the body data
    a tuple called gauge from which is derived:
        a float called spc which is the stitches per centimeter
        a float called rpc which is the rows per centimeter
    a dict called self.pattern_pieces which are uniquely defined by each Garment child to include
        the necessary pattern piece shapes required and referenced by piece names.
    a str called style which is the name of the garment style
    a float called hem_length which is the length of the hem in centimeters.
    """
    def add_to_subplot(self, subplot):  # sets artists for body plots
        for piece in self.pattern_pieces:
            line_color = "magenta"
            line_style = "--"
            if self.pattern_pieces[piece] is not None:
                if piece == "front":
                    line_color = "blue"
                    line_style = ":"
                if piece == "back":
                    line_color = "green"
                    line_style = "-."
                subplot.plot(self.pattern_pieces[piece].x_vals,
                             self.pattern_pieces[piece].y_vals,
                             color=line_color,
                             linewidth=1.0,
                             linestyle=line_style,
                             marker="o",
                             markersize=1.5,
                             alpha=0.5,
                             label=piece)
    #                        scalex=True,
    #                        scaley=True)
                subplot.legend()
                subplot.set_title(self.style + " for " + self.person)

    def create_style_point(self, place, ease, left=True, circumferential=True):
        if left and circumferential:
            point = Point((-self.body[place]["meas"] / 4)*(1+ease/100), self.body[place]["height"])
            return point
        if not left and circumferential:
            point = Point((self.body[place]["meas"] / 4)*(1+ease/100), self.body[place]["height"])
            return point
        if left and not circumferential:
            point = Point((-self.body[place]["meas"] / 2)*(1+ease/100), self.body[place]["height"])
            return point
        if not left and not circumferential:
            point = Point((self.body[place]["meas"] / 2)*(1+ease/100), self.body[place]["height"])
            return point
        raise Exception("class Garment method create_style_point definition has a problem")

    def create_pattern_piece(self, places, piece_key):
        piece_points = []
        for place in places:
            piece_points.append(self.create_style_point(place, places[place]))
        for place in reversed(places):
            piece_points.append(self.create_style_point(place, places[place], left=False))
        piece = PatternPiece(piece_points)
        # update the pattern_pieces dictionary
        self.pattern_pieces[piece_key] = piece

    def write_instructions(self, piece):
        # print(f"the minimum y value in the front piece is {min(self.pattern_pieces["front"].y_vals)}")
        hem_rows = int(np.trunc(self.hem_length * self.rpc))  # results in a number of rows (cm * rows/cm)
        if hem_rows % 2 != 0:  # if hem rows is an odd number
            hem_rows += 1  # make hem rows an even number
        y_vals = np.array(self.pattern_pieces[piece].y_vals)-min(self.pattern_pieces[piece].y_vals)  # adjusts for zero
        total_rows = int(np.trunc(max(y_vals) * self.rpc))
        cp = ["left", "right"]  # carriage position
        cd = ["from left to right", "from right to left"]  # carriage direction
        last_leftmost_needle = 0
        last_rightmost_needle = 0
        count = 0  # the number of rows with the same amount of stitches
        # keep track of knitting in the case of a split
        split = False  # set the default split condition to False
        split_row = False  # set the default split_row condition to False
        for row in range(0, total_rows):  # iterates through each row
            seg_list = []
            segment_intercepts = []
            # find the height in cm corresponding to the row number and adjust for starting at zero
            # height at row zero is the min/self.rpc
            y = (row + min(self.pattern_pieces[piece].y_vals)) / self.rpc
            # print(f"row {row}: looking for {y}.")
            for segment in self.pattern_pieces[piece].segments:
                if segment.contains_y(y):
                    seg_list.append(segment)
                    # keep track of the  x intercepts adjusted for gauge and turned into integer values
                    segment_intercepts.append(int(np.trunc(segment.x_intercept(y) * self.spc)))  # cm * sts/cm = sts
            # list all the unique values and keep track of the repeating ones and their number of duplicates
            needles, counts = np.unique(segment_intercepts, return_counts=True)
            # figure out the leftmost section of knitting
            leftmost_needle = needles[0]
            rightmost_needle = needles[1]
            total_stitches = rightmost_needle-leftmost_needle
            width = 120
            if row == 0:  # cast on with waste yarn and knit hem
                lines = tr.wrap(f"Begin with the carriage on the {cp[1]} side. "
                                f"Place needles from position {leftmost_needle} to position {rightmost_needle}, "
                                f"into working position.  Thread the carriage with waste yarn and fasten a "
                                f"clothespin to the yarn end.  Push the carriage {cd[1]}, to cast on  {total_stitches} "
                                f"total needles.  Push the knitted row against the needle bed and slowly knit one "
                                f"more row.  Hang claw weights along the knitting to evenly distribute weight along "
                                f"the knitting.  Knit for a couple of inches with waste yarn.  With the carriage on "
                                f"the {cp[1]} side, break the waste yarn and secure the tail with a clothespin.  "
                                f"Thread the carriage with your main yarn.  Knit {hem_rows} rows to form the hem. "
                                f"Consider a purl row here??? "
                                "If so, then reverse the carriage positions ", width=width)
                print("")
                for line in lines:
                    print(line)
                print("Set the row counter to 0.")
                print("")
                last_leftmost_needle = leftmost_needle
                last_rightmost_needle = rightmost_needle
            if row == hem_rows:
                print(f"Continue knitting {total_stitches} needles until row counter reads {row}:")
                print("")
                lines = tr.wrap(f"Pull all working needles forward and remove the claw weights.  Taking care not "
                                f"to drop stitches from the extended needles, rehang the hem by placing the purl "
                                f"bumps from the first row of main yarn stitches on the needles.  You will be short "
                                f"one purl bump.  This is expected and will not cause a problem.  Push the knitting "
                                f"against the needle bed and rehang the claw weights.  Loosen the tension and slowly "
                                f"knit 1 row {cd[1]}.  Reset the tension.  At this point, it is okay to carefully "
                                f"remove the waste yarn, but I like to leave it until I take the knitting off the "
                                f"machine.", width=width)
                for line in lines:
                    print(line)
                print("")
                last_leftmost_needle = leftmost_needle
                last_rightmost_needle = rightmost_needle
            if leftmost_needle == last_leftmost_needle and rightmost_needle == last_rightmost_needle:
                count += 1  # keep track of how many rows to knit until something changes
            else:  # once there is a change
                if row % 2 != 0:  # if the row number is odd
                    carriage_position, carriage_direction = cp[0], cd[0]  # the carriage starts on the left
                else:  # row number is even
                    carriage_position, carriage_direction = cp[1], cd[1]  # and carriage starts on the right
                    print(f"Continue knitting until row counter reads {row}:")
                    print("")
                if len(needles) == 2:
                    split = False
                if len(needles) > 2 and split is False:  # compare if this is the first row of a split
                    split_row = True
                    split = True  # if there are more than 2 unique x intercepts there is a split
                if split_row is True:
                    split_counter = row
                    print(f"This is a split row. Cast off between needles {needles[1]} and {needles[2]}.  "
                          f"Place needles {needles[2]} through {needles[3]} on hold.")
                    split_row = False
                else:
                    # if split==True: print("This is a split section")
                    if leftmost_needle != last_leftmost_needle:  # if there is a change on the left
                        if leftmost_needle > last_leftmost_needle:  # if the left is decreasing
                            print(f"\tDecrease {leftmost_needle-last_leftmost_needle} stitch(es) at left edge.")
                        else:
                            print(f"\tIncrease {last_leftmost_needle - leftmost_needle} stitch(es) at left edge.")
                    if rightmost_needle != last_rightmost_needle:  # if there is a change on the right
                        if rightmost_needle < last_rightmost_needle:  # if the right is decreasing
                            print(f"\tDecrease {last_rightmost_needle - rightmost_needle} stitch(es) at right edge.")
                        else:
                            print(f"\tIncrease {rightmost_needle - last_rightmost_needle} stitch(es) at right edge.")
                lines = tr.wrap(f"With carriage on the {carriage_position}, move carriage {carriage_direction}, "
                                f"knitting needles from {leftmost_needle} to {rightmost_needle}. "
                                f"{total_stitches} total stitches.", width=width)
                for line in lines:
                    print(line)
                print("")
                last_leftmost_needle = leftmost_needle
                last_rightmost_needle = rightmost_needle
                # print(f"looking for {y} in ")
                # for segment in self.pattern_pieces[piece].segments: print(segment.seg)
                # print(f"found {len(seg_list)} segments:")
                # for segment in seg_list: print(segment.seg)
                # print(f"needles = {needles} with counts of {counts}")
                # print(f"count = {count}")
                # print(f"leftmost_needle = {leftmost_needle}")
                # print(f"rightmost_needle = {rightmost_needle}")
                # print(f"last_leftmost_needle = {last_leftmost_needle}")
                # print(f"last_rightmost_needle = {last_rightmost_needle}")
                # breakpoint()
                count = 0
        if split is True:
            lines = tr.wrap(f"Cast off remaining stitches.  Reset counter to {split_counter}, and complete "
                            f"opposite side, reversing left and right instructions.", width=width)
            for line in lines:
                print(line)


class PatternPiece(Shape):
    def __init__(self, points):
        self.points = points


class Tshirt(Garment):
    def __init__(self, body, person, gauge=(10, 10)):
        '''
        :param body: type dict this is the body measurement data
        :param person: type str this is the name of the person corresponding to body
        :param gauge: type tuple this is the knit guage in stitches per 10 cm, rows per 10 cm
        '''
        self.person = person
        self.body = body
        self.spc = gauge[0] / 10  # stitches_per_cm
        self.rpc = gauge[1] / 10  # rows_per_cm
        self.pattern_pieces = {
            "front": None,
            "back": None,
            "sleeve": None,
            "left_sleeve": None,
            "right_sleeve": None
        }
        self.style = "T Shirt"
        self.hem_length = 4  # in cm
        self.front_places_with_ease = {
            "highHip": -5,
            # "waist": 10,
            "fullBust": -5,
            "highBust": 0,
            "outerShoulder": 0,
            "shoulderNeck": 0,
            "frontNeck": 0
        }
        self.back_places_with_ease = {
            "highHip": -5,
            # "waist": 10,
            "fullBust": -5,
            "highBust": 0,
            "outerShoulder": 0,
            "shoulderNeck": 0,
            "backNeck": 0
        }
        self.create_pattern_piece(self.front_places_with_ease, piece_key="front")
        self.create_pattern_piece(self.back_places_with_ease, piece_key="back")
