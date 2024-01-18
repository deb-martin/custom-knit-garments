from custom_knit_garments import Dress
from measurements_Debra_Martin import person, body_data

dress = Dress(body_data, person, gauge=(32, 38))
# breakpoint()
if __name__ == "__main__":
    print(f"{dress.style_name} for {person} finished.")
