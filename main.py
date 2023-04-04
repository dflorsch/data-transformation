from datetime import datetime

from src.data_transformation.data import load_csv, clean_projekt_data, export_csv, clean_preis_data


def main():
    start_time = datetime.now()
    print(f"Starting script: {start_time}")

    print("Loading CSV files...")
    preis_input = load_csv(file_name="Preisübersicht")
    projekt_input = load_csv(file_name="Projektzeitauswertung")
    print("Finnished loading. ")

    print("Processing the CSV files...")
    preis_clean = clean_preis_data(file_input=preis_input)
    projekt_clean = clean_projekt_data(file_input=projekt_input)
    print("Processing finnished.")

    print("Exporting the transformed CSV files...")
    export_csv(file_input=preis_clean, file_name="preisübersicht")
    export_csv(file_input=projekt_clean, file_name="projektzeitauswertung")
    print("Exporting finished.")

    end_time = datetime.now()
    print(f"Finnished script in: {end_time - start_time}")


if __name__ == "__main__":
    main()
