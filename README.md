# Teiko Technical Interview
Immune Cell Analysis Dashboard

This repository contains a Python-based pipeline and interactive dashboard built with Streamlit to analyze cell population frequencies in patients treated with miraclib.

## How to Run
You can run the code and reproduce the dashboard outputs using GitHub Codespaces with the following steps:

1. Open this repository in GitHub Codespaces
2. Click the green Code button on GitHub, then select Open with Codespaces > New codespace.
3. Set up the environment. The Codespace comes with Python installed so create and activate a virtual environment:

```
python3 -m venv venv
source venv/bin/activate
```

4. Install dependencies
```
pip install -r requirements.txt
```

Prepare the database
Place your CSV data file (e.g., data.csv) in the repository. Run the data import script from the Python REPL or a script:
```
from TechInterview import import_cell_count_data
import_cell_count_data('cell-count.db', 'cell-count.csv')
```

5. Run the Streamlit dashboard

```
streamlit run app.py 
```

6. Access the app: Use the Ports tab in Codespaces and the dashboard will open in your browser.

## Database Schema & Design
The relational database is designed with three main tables:

1. projects: Stores unique project identifiers to normalize project information and avoid redundancy.
2. people: Contains patient metadata such as subject ID, age, sex, treatment, response status, and a foreign key reference to the project.
3. samples: Stores individual sample measurements including cell counts, sample type, time from treatment start, and a foreign key reference to the patient.

Obviously, with more information this database could be expanded and improved. For now, the projects table could store more specific information about the project and has a one to many relationship with people. The people table contains metadata about each person and has a one to many relationship with samples. Samples store information about the specific sample, such as cell counts and sample type. This could easily scale with many more projects, people, and samples.

Each project can have many people and each person can have many samples. 

<img src="Database Schema.png" alt="Database Schema Diagram" width="600"/>

## Code Structure Overview
The two main files are: 
1. app.py
2. TechInterview.py

I wanted to separate out the visualization code (app.py) from the functional code (TechInterview.py) which is why I separated the files. Within the TechInterview.py file there are four functions, one for each requested component of the technical interview. 

## Dashboard Link
Access the live dashboard here: [Teiko Interview](https://teikointerview.streamlit.app/)
