import fnmatch
import hashlib
import os
from datetime import datetime

import numpy as np
import pandas as pd
from pandas import DataFrame


def load_csv(file_name: str, dir_path: str = None):
    # Set directory if no path is given
    if dir_path is None:
        dir_path = "/Users/.../Input"  # Add path

    # Change working directory
    os.chdir(path=dir_path)

    # Get file from directory that matches the file_name.
    # If a matching files was found save its name in file_path and leave the loop
    file_path = ""
    for file in os.listdir('.'):
        if fnmatch.fnmatch(file, f'*{file_name}*.csv'):
            file_path = file
            break

    # Check if file_path is empty. Exit function if file_path is empty
    if not file_path:
        print("No such file could be found in the choosen directory!")
        return

    # Remove the input file from the directory
    os.remove(f"{file_path}")

    # Read the input file as DataFrame
    file_input = pd.read_csv(file_path, sep=";", encoding="utf-8")

    return file_input


def clean_projekt_data(file_input: DataFrame) -> DataFrame:
    # Drop unnecessary Columns
    file_clean = file_input.drop(
        columns=["Bemerkung", "übergeordnete Vorgänge", "KW", "Ort projektrelevant", "von", "bis"])

    # Rename Columns to fit the Database
    file_clean = file_clean.rename(str.lower, axis='columns').rename(
        columns={"knr": "kundennummer", "mitarbeiter": "mitarbeitende",
                 "ort": "tätigkeitsort", "projekt-nr.": "projektname"})

    # Call the function add_business_unit
    file_clean = add_business_unit(file_input=file_clean)

    # Call the function anomynize_data
    file_clean = anonymize_data(anonymized_data=file_clean)

    # Define tatigkeitort as Büro if nan
    file_clean["tätigkeitsort"] = file_clean["tätigkeitsort"].replace(np.nan, "Büro")

    # Define kundenname - Intern - as Intern
    file_clean["kundenname"] = file_clean["kundenname"].map(lambda x: x.lstrip('- ').rstrip(' -'))

    # Define kundennummer as 999 if nan (intern) and convert column typ to int
    file_clean["kundennummer"] = file_clean["kundennummer"].replace(np.nan, 999).astype(int)

    # convert column "kundennummer" of a DataFrame
    file_clean["kundennummer"] = pd.to_numeric(file_clean["kundennummer"])

    # Generate date for datum
    datelist = []
    for index, row in file_clean.iterrows():
        date = row['datum']

        date_obj = datetime.strptime(date, '%d.%m.%Y')
        datelist.append(date_obj)

    file_clean['datum'] = datelist

    return file_clean


def clean_preis_data(file_input: DataFrame) -> DataFrame:
    # Drop unnecessary Columns
    file_clean = file_input.drop(
        columns=["Vorgang", "Preisgruppe", "Preistabelle", "Tagessatz", "Faktor"])

    # Rename Columns to fit the Database
    file_clean = file_clean.rename(str.lower, axis='columns').rename(
        columns={"mitarbeiter": "mitarbeitende"})

    # Call the function anonymize_data
    file_clean = anonymize_data(file_clean)

    return file_clean


def anonymize_data(anonymized_data: DataFrame) -> DataFrame:
    # Save all unique names of column 'mitarbeitende' in a list
    unique_names = anonymized_data['mitarbeitende'].unique()

    # Generate a hash for every name in the unique_names list
    for name in unique_names:
        hash_object = hashlib.md5(name.encode())
        md5_hash = hash_object.hexdigest()

        # Replace the name with the generated hash
        anonymized_data["mitarbeitende"] = anonymized_data["mitarbeitende"].replace(name, md5_hash)

    return anonymized_data


def add_business_unit(file_input: DataFrame) -> DataFrame:
    mitarbeitende = {
        "employee": "business unit",
        "...": "...",  # Add all Employees
    }

    # Generate a new column 'business unit' by mapping the information of the mitarbeitende column and dictionary
    file_input['business unit'] = file_input['mitarbeitende'].map(mitarbeitende)

    return file_input


def export_csv(file_input: DataFrame, file_name: str):
    dir_path = "/Users/.../Output"

    os.chdir(path=dir_path)

    # Append DataFrame to CSV file if exists, else create new CSV file
    if os.path.exists(f'{file_name}.csv'):
        file_name = f"{file_name}.csv"
        file_input.to_csv(file_name, sep=";", encoding="utf-8", mode='a', header=False, index=False)
    else:
        file_name = f"{file_name}.csv"
        file_input.to_csv(file_name, sep=";", encoding="utf-8", index=False)

    file_name = f"{file_name}.csv"
    file_input.to_csv(file_name, sep=";", encoding="utf-8", index=False)

    file_input.to_csv(os.path.join(path, file_name), sep=";", encoding="utf-8", index=False)
