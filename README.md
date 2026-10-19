
# 🏎️ AI Driver Coach

An F1 performance analysis and lap-time prediction project built with Python, Pandas, Scikit-learn, Plotly and Streamlit.

## Features

- 2024 Formula 1 race results dashboard
- Driver points and finishing-position analysis
- Lap-time consistency and lap-by-lap charts
- Bahrain GP and Saudi Arabian GP comparison
- Driver pace-trend analysis
- Experimental next-lap time prediction
- Model evaluation using MAE and R²

## Tech Stack

- Python
- Pandas
- Scikit-learn
- Streamlit
- Plotly
- Joblib

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

To open the race comparison dashboard:

```bash
streamlit run race_comparison.py
```

## Data

The project uses 2024 F1 race results and recorded lap-time data for the Bahrain and Saudi Arabian Grands Prix.

## Limitations

The lap-time model is experimental. Predictions may vary across circuits and race conditions. The current model does not fully account for tyre strategy, traffic, pit stops or red-flag interruptions.

## Author

Sachin Kumar
