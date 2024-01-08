from custom_knit_garments import *
from measurements_Debra_Martin import person, body_data

tshirt = Tshirt(body_data, person, gauge=(10, 10))
print(f"{tshirt.style_name} for {person} finished.")
