"""
Backend module for the FastAPI application.

This module defines a FastAPI application that serves
as the backend for the project.
"""

from fastapi import FastAPI
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
import pandas as pd

from .mymodules.csv_cleaning import cleancsv1
from .mymodules.csv_cleaning_2 import cleancsv2
from .mymodules.csv_cleaning_3 import cleancsv3

app = FastAPI()

@app.get('/')
def read_root():
    """
    Root endpoint for the backend.

    Returns:
        dict: A simple greeting confirming it's working.
    """
    return {"Test endpoint API": "It's working"}

@app.get('/cleaned_csv_show')
async def read_and_return_cleaned_csv():
    csv_file_path = 'app/regpie-RifugiOpenDa_2296-all.csv'

    # Process the CSV file using the cleancsv1 function
    cleaned_df = cleancsv1(csv_file_path)

    # Convert the processed DataFrame to a dictionary
    cleaned_data = cleaned_df.to_dict(orient='records')

    # Return the cleaned data
    return cleaned_data

@app.get('/cleaned_csv_2_show')
async def read_and_return_cleaned_csv():
    csv_file_path = 'app/Rifugi_Alpini_Escursionistici.csv'

    # Process the CSV file using the cleancsv2 function
    cleaned_df_2 = cleancsv2(csv_file_path)

    # Convert the processed DataFrame to a dictionary
    cleaned_data_2 = cleaned_df_2.to_dict(orient='records')

    # Return the cleaned data
    return cleaned_data_2

@app.get('/cleaned_csv_3_show')
async def read_and_return_cleaned_csv():
    csv_file_path = 'app/Strutture_Ricettive_Alberghiere_e_extra-alberghiere.csv'

    # Process the CSV file using the cleancsv2 function
    cleaned_df_3 = cleancsv3(csv_file_path)

    # Convert the processed DataFrame to a dictionary
    cleaned_data_3 = cleaned_df_3.to_dict(orient='records')

    # Return the cleaned data
    return cleaned_data_3