# STA2453 Project 2 - COVID-19 Socioeconomic Dashboard
Workplace for Winter 2021, STA2453 - Project 2, University of Toronto

This is a dashboard with three different tabs that display financial & social factors that are related to COVID-19.

## Instructions

1. Clone the repo inside a new virtual environment.
2. Navigate to the cloned directory and install the required packages using the following command:

```
pip install -r requirements.txt
```

3. Once in the root directory, navigate to the directory `./code`. 
4. Run the command:

```
python3 app.py
```
5. Copy and paste the http link (`http://127.0.0.1:8000/`) from the terminal message into a web browser and run.

## File Directory

### Code:
1. `app.py` contains all the dashboard code. 
2. `./code/data_import` contains all the code to import the data and clean the data. The import stage is separated by tab, with a file for finance data, vaccine data, and policy data.

### Data:
1. `./clean` contains all the cleaned data.
2. `./raw` contains all the raw data.

