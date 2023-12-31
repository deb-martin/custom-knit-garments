import matplotlib
import matplotlib.pyplot as plt
from points_and_segs import *
from measurements_Debra_Martin import person, body

body_shape = Body(body, person)
tshirt = Tshirt(body, person, gauge=[10, 10])
# fitted_t = Tshirt_fitted(body, person)
# plot_canvas = matplotlib.figure.Figure(figsize=[10, 10])
# subplots = []
# for x in range(1, 5):
#     subplot = plot_canvas.add_subplot(2, 2, x)  # creates a subplot structure returns axes
#     subplots.append(subplot)
# for subplot in subplots:
#     subplot.axis(xmin=-100, xmax=100)
#     subplot.axis(ymin=-120, ymax=80)
#     subplot.xaxis.set_major_locator(matplotlib.ticker.LinearLocator(21))
#     subplot.yaxis.set_major_locator(matplotlib.ticker.LinearLocator(21))
#     body_shape.add_to_subplot(subplot=subplot)
tshirt.write_instructions("front")


# tshirt.add_to_subplot(subplot=subplots[2])
# fitted_t.add_to_subplot(subplot=subplots[3])
# plot_canvas.savefig("testplot.svg", format="svg")
breakpoint()
print(f"{tshirt.style} for {person} finished.")
