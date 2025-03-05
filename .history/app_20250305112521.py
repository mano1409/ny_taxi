import sys
from pathlib import Path
import zipfile
import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st
from branca.colormap import LinearColormap
from streamlit_folium import st_folium

# Configure data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_shape_data_file(
    data_dir, url="https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip"
):
    """Download, extract, and load a shapefile as a GeoDataFrame."""
    zip_path = data_dir / "taxi_zones.zip"
    extract_path = data_dir / "taxi_zones"
    shapefile_path = extract_path / "taxi_zones.shp"

    if not zip_path.exists():
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(zip_path, "wb") as f:
            f.write(response.content)

    if not shapefile_path.exists():
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

    return gpd.read_file(shapefile_path).to_crs("epsg:4326")

def create_taxi_map(shapefile_path, prediction_data):
    """Create an interactive NYC taxi zone map with demand predictions."""
    nyc_zones = gpd.read_file(shapefile_path)
    nyc_zones = nyc_zones.merge(
        prediction_data, left_on="LocationID", right_on="pickup_location_id", how="left"
    ).fillna(0)

    m = folium.Map(location=[40.7128, -74.0060], zoom_start=10, tiles="cartodbpositron")
    colormap = LinearColormap(["#FFEDA0", "#E31A1C"], vmin=0, vmax=nyc_zones["predicted_demand"].max())
    colormap.add_to(m)

    folium.GeoJson(
        nyc_zones.to_json(),
        style_function=lambda feature: {
            "fillColor": colormap(feature["properties"]["predicted_demand"]),
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.7,
        },
        tooltip=folium.GeoJsonTooltip(fields=["zone", "predicted_demand"]),
    ).add_to(m)

    return m

# Streamlit UI
st.title("NYC Yellow Taxi Ride Demand Prediction")
current_date = pd.Timestamp.now(tz="Etc/UTC")
st.header(f'{current_date.strftime("%Y-%m-%d %H:%M:%S")}')

st.sidebar.header("Progress")
progress_bar = st.sidebar.progress(0)

st.spinner(text="Loading taxi zones...")
geo_df = load_shape_data_file(DATA_DIR)
progress_bar.progress(1 / 3)

st.spinner(text="Fetching mock predictions...")
# Mock Data
predictions = pd.DataFrame({
    "pickup_location_id": geo_df["LocationID"],
    "predicted_demand": pd.Series(range(len(geo_df))).sample(len(geo_df)).values,
})
progress_bar.progress(2 / 3)

st.spinner(text="Creating map...")
map_obj = create_taxi_map(DATA_DIR / "taxi_zones" / "taxi_zones.shp", predictions)
st_folium(map_obj, width=800, height=600)
progress_bar.progress(3 / 3)

st.subheader("Top 10 Predicted Demand Locations")
st.dataframe(predictions.sort_values("predicted_demand", ascending=False).head(10))
