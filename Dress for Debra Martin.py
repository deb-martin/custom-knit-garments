from custom_knit_garments import Dress
from measurements_Debra_Martin import person, body_data

dress = Dress(body_data, person, gauge=(32, 38))
# breakpoint()
if __name__ == "__main__":
    print(f"This design requires {dress.total_yarn_meters} "
          f"meters of yarn at your chosen gauge of {dress.gauge_string}.")
    print(f"{dress.style_name} for {person} finished.")
