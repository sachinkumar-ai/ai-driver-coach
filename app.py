
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="AI Driver Coach",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ AI Driver Coach")
st.caption("Formula 1 Performance Analysis Dashboard | 2024 Season")

# Load data
df = pd.read_csv("data/f1_2024_season.csv")

df["Position"] = pd.to_numeric(df["Position"], errors="coerce")
df["Grid"] = pd.to_numeric(df["Grid"], errors="coerce")
df["Points"] = pd.to_numeric(df["Points"], errors="coerce")

# Sidebar filters
st.sidebar.header("Race Filters")

races = sorted(df["Race"].dropna().unique())
selected_race = st.sidebar.selectbox(
    "Select a Grand Prix",
    ["Full Season"] + races
)

if selected_race == "Full Season":
    filtered_df = df.copy()
else:
    filtered_df = df[df["Race"] == selected_race].copy()

# Summary metrics
col1, col2, col3 = st.columns(3)

col1.metric("Race Records", len(filtered_df))
col2.metric("Drivers", filtered_df["Driver"].nunique())
col3.metric("Total Points", round(filtered_df["Points"].sum(), 1))

st.divider()

# Driver points
st.subheader("Driver Performance")

driver_points = (
    filtered_df.groupby("Driver", as_index=False)["Points"]
    .sum()
    .sort_values("Points", ascending=False)
)

fig = px.bar(
    driver_points,
    x="Points",
    y="Driver",
    orientation="h",
    title="Points by Driver",
    color="Points",
    color_continuous_scale="RdYlGn"
)

fig.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig, use_container_width=True)

# Position gain analysis
st.subheader("Starting Grid vs Finishing Position")

position_df = filtered_df.dropna(
    subset=["Grid", "Position"]
).copy()

position_df["Positions Gained"] = (
    position_df["Grid"] - position_df["Position"]
)

fig2 = px.scatter(
    position_df,
    x="Grid",
    y="Position",
    color="Driver",
    hover_data=["Race", "Team", "Positions Gained"],
    title="Starting Position vs Finishing Position"
)

st.plotly_chart(fig2, use_container_width=True)


# Individual Driver Analysis
st.divider()
st.subheader("🔎 Individual Driver Analysis")

drivers = sorted(df["Driver"].dropna().unique())

selected_driver = st.selectbox(
    "Select a Driver",
    drivers
)

driver_df = df[df["Driver"] == selected_driver].copy()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Points",
    round(driver_df["Points"].sum(), 1)
)

col2.metric(
    "Races Participated",
    driver_df["Race"].nunique()
)

col3.metric(
    "Average Finish",
    round(driver_df["Position"].mean(), 2)
)

st.write(f"### {selected_driver} — Race-by-Race Performance")

fig_driver = px.line(
    driver_df.sort_values("Round"),
    x="Round",
    y="Points",
    markers=True,
    title=f"{selected_driver}: Points per Race",
    hover_data=["Race", "Position", "Team"]
)

st.plotly_chart(fig_driver, use_container_width=True)

st.dataframe(
    driver_df[
        ["Round", "Race", "Grid", "Position", "Points", "Status"]
    ].sort_values("Round"),
    use_container_width=True,
    hide_index=True
)


# Data table
st.subheader("Race Results")
st.dataframe(
    filtered_df[
        ["Race", "Driver", "Team", "Grid", "Position", "Points", "Status"]
    ].sort_values(["Race", "Position"], na_position="last"),
    use_container_width=True,
    hide_index=True
)
 
st.header("🏁 Driver Consistency Analysis")

lap_df = pd.read_csv("data/bahrain_lap_times.csv")

def to_seconds(lap_time):
    minutes, seconds = lap_time.split(":")
    return int(minutes) * 60 + float(seconds)

lap_df["LapTimeSeconds"] = lap_df["LapTime"].apply(to_seconds)

consistency = (
    lap_df.groupby("Driver")["LapTimeSeconds"]
    .std()
    .sort_values()
)

st.write("Lower variation means more consistent lap times.")

st.bar_chart(consistency)

st.subheader("Average Lap Time by Driver")

average_times = (
    lap_df.groupby("Driver")["LapTimeSeconds"]
    .mean()
    .sort_values()
)

st.bar_chart(average_times)


st.header("🏎️ Lap-by-Lap Driver Performance")

drivers = sorted(lap_df["Driver"].dropna().unique())

selected_driver = st.selectbox(
    "Select a Driver",
    drivers,
    key="lap_driver_selector"
)

driver_laps = lap_df[
    lap_df["Driver"] == selected_driver
].copy()

driver_laps = driver_laps.sort_values("Lap")

st.write(f"Selected Driver: {selected_driver}")
st.write(f"Total recorded laps: {driver_laps['Lap'].nunique()}")

st.line_chart(
    driver_laps.set_index("Lap")["LapTimeSeconds"]
)

st.subheader("Lap Details")

st.dataframe(
    driver_laps[["Lap", "LapTime", "Position"]],
    use_container_width=True
)


import joblib

st.header("🤖 AI Next Lap-Time Predictor")

model = joblib.load("models/lap_time_model.pkl")

driver_options = sorted(lap_df["Driver"].dropna().unique())

selected_driver = st.selectbox(
    "Select Driver",
    driver_options,
    key="next_lap_driver"
)

driver_history = (
    lap_df[lap_df["Driver"] == selected_driver]
    .copy()
    .sort_values("Lap")
)

def lap_seconds(lap_time):
    minutes, seconds = lap_time.split(":")
    return int(minutes) * 60 + float(seconds)

driver_history["LapTimeSeconds"] = (
    driver_history["LapTime"].apply(lap_seconds)
)

if len(driver_history) >= 3:
    previous_times = driver_history["LapTimeSeconds"].tail(3).tolist()

    previous_lap = previous_times[-1]
    previous_three_average = sum(previous_times) / 3

    next_lap_number = int(driver_history["Lap"].max()) + 1

    prediction_input = pd.DataFrame([{
        "Lap": next_lap_number,
        "PreviousLapTime": previous_lap,
        "Previous3LapAverage": previous_three_average
    }])

    if st.button("Predict Next Lap Time"):
        predicted_seconds = model.predict(prediction_input)[0]

        minutes = int(predicted_seconds // 60)
        seconds = predicted_seconds % 60

        st.success(
            f"Estimated Lap Time: {minutes}:{seconds:05.2f}"
        )
        st.caption(
            "Experimental estimate based on previous laps. "
            "Actual lap times may differ due to tyres, traffic, "
            "pit stops and race conditions."
        )
else:
    st.warning("This driver does not have enough lap-time data.")


st.header("📊 ML Model Performance")

import json
from pathlib import Path
from sklearn.metrics import mean_absolute_error, r2_score

evaluation_df = pd.read_csv("data/bahrain_lap_times.csv")

def convert_lap_seconds(value):
    minutes, seconds = value.split(":")
    return int(minutes) * 60 + float(seconds)

evaluation_df["LapTimeSeconds"] = (
    evaluation_df["LapTime"].apply(convert_lap_seconds)
)

evaluation_df = evaluation_df.sort_values(["Driver", "Lap"])

evaluation_df["PreviousLapTime"] = (
    evaluation_df.groupby("Driver")["LapTimeSeconds"].shift(1)
)

evaluation_df["Previous3LapAverage"] = (
    evaluation_df.groupby("Driver")["LapTimeSeconds"]
    .transform(lambda s: s.shift(1).rolling(3, min_periods=3).mean())
)

evaluation_df = evaluation_df.dropna(
    subset=["PreviousLapTime", "Previous3LapAverage"]
).copy()

split_lap = int(evaluation_df["Lap"].max() * 0.7)
test_df = evaluation_df[evaluation_df["Lap"] > split_lap].copy()

features = ["Lap", "PreviousLapTime", "Previous3LapAverage"]

evaluation_model = joblib.load("models/lap_time_model.pkl")
test_df["PredictedLapTime"] = evaluation_model.predict(test_df[features])

mae = mean_absolute_error(
    test_df["LapTimeSeconds"], test_df["PredictedLapTime"]
)
r2 = r2_score(
    test_df["LapTimeSeconds"], test_df["PredictedLapTime"]
)

col1, col2 = st.columns(2)
col1.metric("Mean Absolute Error", f"{mae:.3f} sec")
col2.metric("R² Score", f"{r2:.3f}")

test_df["AbsoluteError"] = (
    test_df["LapTimeSeconds"] - test_df["PredictedLapTime"]
).abs()

st.subheader("Actual vs Predicted Lap Times")

chart_df = test_df[
    test_df["Driver"] == "max_verstappen"
].sort_values("Lap")

st.line_chart(
    chart_df.set_index("Lap")[
        ["LapTimeSeconds", "PredictedLapTime"]
    ]
)

st.subheader("Prediction Details")
st.dataframe(
    test_df[
        ["Driver", "Lap", "LapTimeSeconds", "PredictedLapTime", "AbsoluteError"]
    ].round(3),
    use_container_width=True
)
