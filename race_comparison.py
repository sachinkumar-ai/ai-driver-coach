
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="F1 Race Comparison",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ F1 Race Comparison")
st.caption("Bahrain GP vs Saudi Arabian GP — 2024")

def to_seconds(value):
    parts = str(value).split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    return float(parts[0])

bahrain = pd.read_csv("data/bahrain_lap_times.csv")
saudi = pd.read_csv("data/saudi_lap_times.csv")

bahrain["Race"] = "Bahrain GP"
saudi["Race"] = "Saudi Arabian GP"

df = pd.concat([bahrain, saudi], ignore_index=True)
df["LapTimeSeconds"] = df["LapTime"].apply(to_seconds)

driver_options = sorted(df["Driver"].dropna().unique())

selected_drivers = st.multiselect(
    "Select drivers to compare",
    driver_options,
    default=driver_options[:3]
)

comparison = df[df["Driver"].isin(selected_drivers)].copy()

st.subheader("Average Lap Time by Driver and Race")

summary = (
    comparison.groupby(["Race", "Driver"], as_index=False)
    ["LapTimeSeconds"].mean()
)

fig = px.bar(
    summary,
    x="Driver",
    y="LapTimeSeconds",
    color="Race",
    barmode="group",
    title="Average Recorded Lap Time",
    labels={"LapTimeSeconds": "Average lap time (seconds)"}
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Lap-by-Lap Comparison")

fig2 = px.line(
    comparison,
    x="Lap",
    y="LapTimeSeconds",
    color="Race",
    line_dash="Race",
    facet_col="Driver",
    facet_col_wrap=2,
    title="Lap Times Across Both Races",
    labels={"LapTimeSeconds": "Lap time (seconds)"}
)

st.plotly_chart(fig2, use_container_width=True)

st.caption(
    "Note: Red-flag periods, pit stops and unusual recorded laps "
    "can affect averages. These are recorded times, not pure pace estimates."
)

st.divider()
st.header("🏆 Driver Performance Ranking")

ranking = (
    comparison.groupby(["Race", "Driver"])
    .agg(
        Average_Lap=("LapTimeSeconds", "mean"),
        Fastest_Lap=("LapTimeSeconds", "min"),
        Consistency=("LapTimeSeconds", "std"),
        Recorded_Laps=("LapTimeSeconds", "count")
    )
    .reset_index()
)

ranking["Average_Lap"] = ranking["Average_Lap"].round(3)
ranking["Fastest_Lap"] = ranking["Fastest_Lap"].round(3)
ranking["Consistency"] = ranking["Consistency"].round(3)

ranking = ranking.sort_values(
    ["Race", "Average_Lap"],
    ascending=[True, True]
)

st.dataframe(
    ranking,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Lower average lap time means faster recorded laps. "
    "Lower consistency value means less variation in lap times. "
    "Pit stops and unusual laps can affect both measures."
)


st.divider()
st.header("📉 Lap-Time Degradation Analysis")

degradation_drivers = st.multiselect(
    "Select drivers for degradation analysis",
    driver_options,
    default=driver_options[:3],
    key="degradation_drivers"
)

degradation_race = st.selectbox(
    "Select race",
    ["Bahrain GP", "Saudi Arabian GP"],
    key="degradation_race"
)

degradation_df = df[
    (df["Race"] == degradation_race)
    & (df["Driver"].isin(degradation_drivers))
].copy()

degradation_df = degradation_df.sort_values(["Driver", "Lap"])

# Compare each lap with the driver's previous lap
degradation_df["LapTimeChange"] = (
    degradation_df.groupby("Driver")["LapTimeSeconds"].diff()
)

fig3 = px.line(
    degradation_df,
    x="Lap",
    y="LapTimeSeconds",
    color="Driver",
    markers=True,
    title=f"Lap-Time Trend — {degradation_race}",
    labels={
        "Lap": "Lap Number",
        "LapTimeSeconds": "Lap Time (seconds)"
    }
)

st.plotly_chart(fig3, use_container_width=True)

st.subheader("Lap-Time Change from Previous Lap")

fig4 = px.line(
    degradation_df,
    x="Lap",
    y="LapTimeChange",
    color="Driver",
    markers=True,
    title="Change in Lap Time (seconds)",
    labels={"LapTimeChange": "Change in seconds"}
)

st.plotly_chart(fig4, use_container_width=True)

st.caption(
    "Positive change = slower than the previous lap. "
    "Negative change = faster than the previous lap. "
    "Pit stops, traffic, safety cars and red flags can affect these trends."
)

st.divider()
st.header("🤖 AI Driver Pace Coach")

coach_race = st.selectbox(
    "Select race for coaching",
    ["Bahrain GP", "Saudi Arabian GP"],
    key="coach_race"
)

coach_drivers = sorted(
    df[df["Race"] == coach_race]["Driver"].dropna().unique()
)

coach_driver = st.selectbox(
    "Select driver",
    coach_drivers,
    key="coach_driver"
)

coach_df = df[
    (df["Race"] == coach_race)
    & (df["Driver"] == coach_driver)
].copy()

coach_df = coach_df.sort_values("Lap")

if len(coach_df) >= 6:
    recent = coach_df.tail(6).copy()
    first_three = recent["LapTimeSeconds"].iloc[:3].mean()
    last_three = recent["LapTimeSeconds"].iloc[3:].mean()

    change = last_three - first_three

    col1, col2, col3 = st.columns(3)

    col1.metric("Earlier 3-Lap Average", f"{first_three:.3f} sec")
    col2.metric("Latest 3-Lap Average", f"{last_three:.3f} sec")
    col3.metric(
        "Pace Change",
        f"{change:+.3f} sec",
        delta=f"{-change:+.3f} sec",
        delta_color="normal"
    )

    if change < -0.3:
        st.success("Pace trend: Improving 🟢")
        st.write("The latest three laps are faster on average.")
    elif change > 0.3:
        st.warning("Pace trend: Slowing 🔴")
        st.write(
            "The latest three laps are slower. "
            "Check traffic, pit stops and race conditions."
        )
    else:
        st.info("Pace trend: Relatively stable 🟡")
        st.write("The two three-lap averages are close.")

    st.caption(
        "This is a simple pace-trend estimate, not a tyre diagnosis. "
        "Unusual laps and race interruptions can affect the result."
    )
else:
    st.warning("Not enough recorded laps for this analysis.")
