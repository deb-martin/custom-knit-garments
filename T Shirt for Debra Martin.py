from custom_knit_garments import Tshirt
from measurements_Debra_Martin import person, body_data

tshirt = Tshirt(body_data, person, gauge=(32, 38))
# breakpoint()

if __name__ == "__main__":
    print(f"This design requires {tshirt.total_yarn_meters} "
          f"meters of yarn at your chosen gauge of {tshirt.gauge_string}.")
    print(f"{tshirt.style_name} for {person} finished.")

