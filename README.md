# MP2 Data Processing API

This API gives the user an interface where they can upload, view, and process datasets using the pipeline created in MP1 and a given configuration.

## Description

This program uses uvicorn and FastAPI to run the API application and connect endpoints.

The user can get the health of the program, upload and store a .csv data set, retrieve a stored dataset based on the given ID, and process a dataset based on a given configuration (json format).

The processing behind the data is done by the previously established mp1 pipeline.

## Use

Packages used are listed in requirements.txt.

To launch the application run:

>python -m uvicorn main:app --reload

and then go to http://127.0.0.1:8000/docs to try out the functions.

