import matplotlib
import matplotlib.pyplot as plt
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
    def all_x_vals(self):  # may not ever use this
        x_intercepts = []
        count = min(self.y_vals)
        while count <= max(self.y_vals):
            x_intercepts.append(self.x_intercept(count))
            count += 1
        return x_intercepts


# TODO: to eliminate warnings, should I consider using a constructor here and calling a super init in subclasses?
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
        segments = []
        for pair in itertools.pairwise(self.points):
            segments.append(Seg(pair[0], pair[1]))
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
                     linewidth=1.0,
                     marker=".",
                     markersize=1.5,
                     alpha=1.0,
                     label="body")
        subplot.legend()
        subplot.grid(visible=True, which='both', color='grey', linestyle='-.', linewidth=0.35)
        subplot.set_title("Garment for " + self.person)


class Garment:
    """
    class Garment has no init because it is used as a super class solely to define methods
    for all its subclasses. Garment subclasses are used to define all the different styles.
    EXAMPLES are Tshirt, Dress, and Cardigan
    All Garment objects are created by subclasses, therefore, Garment needs no constructor.
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

    # TODO: change to reflect that the pieces come from the required_pattern_pieces dictionary

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

    def add_garment_to_subplot(self, subplot):  # sets artists for body plots
        for piece in self.style:
            line_color = "magenta"
            line_style = "--"
            if piece == "front":
                line_color = "blue"
                line_style = ":"
            if piece == "back":
                line_color = "green"
                line_style = "-."
            subplot.plot(self.style[piece]["pattern_piece"].x_vals,
                         self.style[piece]["pattern_piece"].y_vals,
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
            subplot.set_title(self.style_name + " for " + self.person)

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

    def create_pattern_piece(self, places):
        points = [self.create_style_point(place, places[place]) for place in places]
        piece_points = []
        for place in places:
            piece_points.append(self.create_style_point(place, places[place]))
        for place in reversed(places):
            piece_points.append(self.create_style_point(place, places[place], left=False))
        piece = PatternPiece(piece_points)
        return piece

    def write_instructions(self, piece):  # refers to the self.pattern_pieces dict by key piece
        # def create_blank_needle_chart():
        #     needle_position_chart = {}  # create blank needle position chart
        #     # create list of all needles on the machine and set them to False
        #     # Do needle_position_chart[row][needle_number]=True to change the setting
        #     needle_positions = {}
        #     for needle_number in range(-100, 101):
        #         if needle_number != 0:
        #             needle_positions.update({needle_number: False})
        #     for row in range(0, total_rows):  # iterates through each row
        #         needle_position_chart.update({row: needle_positions})
        #     return needle_position_chart

        def write_instructions_for_cast_on():
            lines = tr.wrap(f"Begin with the carriage on the {cp[1]} side. "
                            f"Place needles from position {leftmost_needle} to position {rightmost_needle}, "
                            f"into working position.  Thread the carriage with waste yarn and fasten a "
                            f"clothespin to the yarn end.  Push the carriage {cd[1]}, to cast on  {total_stitches} "
                            f"total needles.  Push the knitted row against the needle bed and slowly knit one "
                            f"more row.  Hang claw weights along the knitting to evenly distribute weight along "
                            f"the knitting.  Knit for a couple of inches with waste yarn.  With the carriage on "
                            f"the {cp[1]} side, break the waste yarn and secure the tail with a clothespin.  "
                            f"Thread the carriage with your main yarn.  ", width=width)
            print("Instructions for cast on:\n", file=file_name)
            for line in lines:
                print(line, file=file_name)
            print("Set the row counter to 0.\n", file=file_name)

        def write_instructions_for_hem():
            print(f"Continue knitting {total_stitches} needles until row counter reads {row}:", file=file_name)
            lines = tr.wrap(f"Knit {hem_rows} rows to form the hem. Consider a purl row here??? "
                            "If so, then reverse the carriage positions "
                            "Pull all working needles forward and remove the claw weights.  Taking care not "
                            f"to drop stitches from the extended needles, rehang the hem by placing the purl "
                            f"bumps from the first row of main yarn stitches on the needles.  You will be short "
                            f"one purl bump.  This is expected and will not cause a problem.  Push the knitting "
                            f"against the needle bed and rehang the claw weights.  Loosen the tension and slowly "
                            f"knit 1 row {cd[1]}.  Reset the tension.  At this point, it is okay to carefully "
                            f"remove the waste yarn, but I like to leave it until I take the knitting off the "
                            f"machine.", width=width)
            for line in lines:
                print(line, file=file_name)

        def write_split_row_instructions():
            print(f"This is a split row. Cast off between needles {needles[1]} and {needles[2]}.  "
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

        # def populate_needle_position_chart():
        #     for row in needle_intercepts:
        #         for needle in range(needle_intercepts[row][0], (needle_intercepts[row][1]+1), 1):
        #             if needle != 0:
        #                 needle_position_chart[row][needle] = True
        #         if len(needle_intercepts[row]) > 2:
        #             for needle in range(needle_intercepts[row][2], (needle_intercepts[row][3]+1), 1):
        #                 if needle != 0:
        #                     needle_position_chart[row][needle] = True
        #         print(f"Row: {row}")
        #         print(f"needle_intercepts[{row}]: {needle_intercepts[row]}")
        #         print(f"needle_position_chart[{row}]: {needle_position_chart[row]}")
        #     return needle_position_chart

        file_name = open(self.style + piece + "_for_" + self.person + ".txt", "w")
        hem_rows = int(np.trunc(self.hem_length * self.rpc))  # results in a number of rows (cm * rows/cm)
        y_vals = np.array(self.pattern_pieces[piece].y_vals) - min(
            self.pattern_pieces[piece].y_vals)  # adjusts for zero
        total_rows = int(max(y_vals) * self.rpc)
        cp = ["left", "right"]  # carriage position
        cd = ["from left to right", "from right to left"]  # carriage direction
        last_leftmost_needle = 0
        last_rightmost_needle = 0
        count = 0  # the number of rows with the same amount of stitches
        split = False  # set the default split condition to False
        split_row = False  # set the default split_row condition to False
        # needle_position_chart = create_blank_needle_chart()
        needle_intercepts = {}  # dict of rows and their unique needle numbers EX: {0: array([-23, 23])}
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
                    segment_intercepts.append(int(segment.x_intercept(y) * self.spc))  # cm * sts/cm = sts
            # list all the unique values and keep track of the repeating ones and their number of duplicates
            needles, counts = np.unique(segment_intercepts, return_counts=True)
            needle_intercepts.update({row: needles})
            leftmost_needle, rightmost_needle = needles[0], needles[1]  # leftmost section of knitting
            total_stitches = rightmost_needle - leftmost_needle
            width = 120  # this is the number of characters for text wrapping
            if row == 0:
                write_instructions_for_cast_on()
                last_leftmost_needle = leftmost_needle
                last_rightmost_needle = rightmost_needle
            if hem_rows > 0 and row == hem_rows:
                write_instructions_for_hem()
                last_leftmost_needle = leftmost_needle
                last_rightmost_needle = rightmost_needle
            if leftmost_needle == last_leftmost_needle and rightmost_needle == last_rightmost_needle:
                count += 1  # keep track of how many rows to knit until something changes
            else:  # once there is a change
                if row % 2 != 0:  # if the row number is odd
                    carriage_position, carriage_direction = cp[0], cd[0]  # the carriage starts on the left
                else:  # row number is even
                    carriage_position, carriage_direction = cp[1], cd[1]  # and carriage starts on the right
                print(f"\nContinue knitting until row counter reads {row}:", file=file_name)
                if len(needles) == 2:
                    split = False
                if len(needles) > 2 and split is False:  # compare if this is the first row of a split
                    split_row = True
                    split = True  # if there are more than 2 unique x intercepts there is a split
                if split_row is True:
                    split_counter = row
                    write_split_row_instructions()
                    split_row = False
                else:
                    write_change_instructions()
                lines = tr.wrap(f"With carriage on the {carriage_position}, move carriage {carriage_direction}, "
                                f"knitting needles from {leftmost_needle} to {rightmost_needle}. "
                                f"{total_stitches} total stitches.", width=width)
                for line in lines:
                    print(line, file=file_name)
                last_leftmost_needle = leftmost_needle
                last_rightmost_needle = rightmost_needle
                count = 0
        if split is True:
            lines = tr.wrap(f"Cast off remaining stitches.  Reset counter to {split_counter}, and complete "
                            f"opposite side, reversing left and right instructions.", width=width)
            for line in lines:
                print(line, file=file_name)
        file_name.close()
        # populate_needle_position_chart()
        # print(needle_position_chart[58])


class PatternPiece(Shape):
    def __init__(self, points):
        self.points = points
        # self.points = []
        # for place in places:
        #     self.points.append(self.create_style_point(place, places[place]))
        # for place in reversed(places):
        #     self.points.append(self.create_style_point(place, places[place], left=False))


class Chart:
    def __init__(self, gauge, piece_shape):
        """returns an object that includes a row by row list of row status
        (cast_on, hem, split, regular, change - anything relating to instructions for that row)
        and associated needle state for all 200 needles on the machine
        can return a shape object scaled and truncated for applied gauge which in turn can
        return a list of x stitch values for plotting
        return a list of y row values for plotting
        convert itself back to cm with steps for row increases and decreases???
        The Chart object shall be passed to the write_instructions method.
        It should contain all the information necessary for writing the pattern instructions
        It needs to know the pattern_piece shape, the guage, and the hem length for itself.
        All of this could come from the required_pattern_pieces dictionary defined in the style module
        """

        self.gauge = gauge
        self.piece_shape = piece_shape

    def create_needle_charts(self, pattern_pieces):
        """makes a needle_chart object for each pattern_piece
        which contains the needles necessary for each row"""


class Tshirt(Garment):
    def __init__(self, body_data, person, gauge=(10, 10)):
        '''
        :param body_data: imported from measurement data file
        :param person: imported from measurement data file
        :param gauge: type tuple stitches per 10 cm, rows per 10 cm
        '''
        self.person = person
        self.body_data = body_data
        self.body_shape = Body(body_data, person)
        self.spc = gauge[0] / 10  # stitches_per_cm
        self.rpc = gauge[1] / 10  # rows_per_cm
        self.body_shape = Body(body_data, person)
        front_places_with_ease_percent = {
            "highHip": -5,
            # "waist": 10,
            "fullBust": -5,
            "highBust": 0,
            "outerShoulder": 0,
            "shoulderNeck": 0,
            "frontNeck": 0
        }
        back_places_with_ease_percent = {
            "highHip": -5,
            # "waist": 10,
            "fullBust": -5,
            "highBust": 0,
            "outerShoulder": 0,
            "shoulderNeck": 0,
            "backNeck": 0
        }
        self.required_pattern_pieces = {
            "front": {"places_with_ease": front_places_with_ease_percent, "hem_length": 5, "gauge": gauge},
            "back": {"places_with_ease": back_places_with_ease_percent, "hem_length": 5, "gauge": gauge}
        }
        self.style_name = "T Shirt"
        self.style = {piece_name:
            {"pattern_piece": self.create_pattern_piece(
                self.required_pattern_pieces[piece_name]["places_with_ease"]),
                # in cm - used for plotting over the body
                "hem_length_cm": self.required_pattern_pieces[piece_name]["hem_length"],
                "needle_chart": {},  # in needles and rows with gauge applied
                "instructions": {}  # some text file???? or other collection of text blocks
            } for piece_name in self.required_pattern_pieces}
        plot_canvas = matplotlib.figure.Figure(figsize=[10, 10])
        subplots = [plot_canvas.add_subplot(1, 1, x) for x in range(1, 2)]
        for subplot in subplots:
            subplot.axis(xmin=-100, xmax=100)
            subplot.axis(ymin=-120, ymax=80)
            subplot.xaxis.set_major_locator(matplotlib.ticker.LinearLocator(21))
            subplot.yaxis.set_major_locator(matplotlib.ticker.LinearLocator(21))
            self.body_shape.add_to_subplot(subplot=subplot)
        self.add_garment_to_subplot(subplot=subplots[0])
        plot_canvas.savefig(fname=f"{self.style_name} for {person}.svg", format="svg")
        # need to make PDF with images and instructions
