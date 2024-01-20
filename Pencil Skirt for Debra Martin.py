from custom_knit_garments import Pencil_Skirt
from measurements_Debra_Martin import person, body_data

ps = Pencil_Skirt(body_data, person, gauge=(32, 38))
# breakpoint()

if __name__ == "__main__":
    print(f"This design requires {ps.total_yarn_meters} "
          f"meters of yarn at your chosen gauge of {ps.gauge_string}.")
    print(f"{ps.style_name} for {person} finished.")

