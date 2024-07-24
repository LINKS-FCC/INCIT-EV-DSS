import os.path

import streamlit as st
from slugify import slugify

from ubm.car_parking import calculate_car_parked
from ubm.enact_pop import add_enact_pop_stat_to_gdf
from ubm.mobility import get_trips_info
from ubm.plotting import plot_day_night
from ubm.surveys import calculate_bevs_phevs_percentage
from ubm.utils.stuff import load_yaml
from ubm.zoning import shapefile_path_to_geodataframe
import pandas as pd

class Toc:

    def __init__(self):
        self._items = []
        self._links = {}
        self._placeholder = None

    def title(self, text):
        self._markdown(text, "h1")

    def header(self, text):
        self._markdown(text, "h2", " " * 2)

    def subheader(self, text):
        self._markdown(text, "h3", " " * 4)

    def placeholder(self, sidebar=False):
        st.sidebar.title("Table of contents")
        self._placeholder = st.sidebar.title(
            "Table of contents") if sidebar else st.empty()

    def generate(self):
        if self._placeholder:
            self._placeholder.markdown(
                "\n".join(self._items), unsafe_allow_html=True)

    def get_link(self, text):
        return self._links[text]

    def _markdown(self, text, level, space=""):
        key = slugify(text)

        st.markdown(f"<{level} id='{key}'>{text}</{level}>",
                    unsafe_allow_html=True)
        self._items.append(f"{space}* <a href='#{key}'>{text}</a>")
        self._links[text] = (f"[{text}](#{key})")

def plot_cache(input_data, behaviour):
    # Loading Zoning and augmenting it with JRC's ENACT-POP data
    filename = input_data['zoning_shp_path']
    gdf = shapefile_path_to_geodataframe(filename)
    gdf = add_enact_pop_stat_to_gdf(gdf)

    # Get Information about Trips and Vehicles
    urban_trips, in_trips, out_trips, avg_n_trips = get_trips_info(input_data)
    gdf = calculate_bevs_phevs_percentage(gdf, input_data)
    gdf = calculate_car_parked(gdf, urban_trips, in_trips, out_trips, avg_n_trips)
    fig = plot_day_night(gdf, "EV", "day_parking_plot_bevs", "night_parking_plot_bevs")
    return fig

if __name__ == '__main__':
    input = "input/weekday_turin_1.yaml"
    config = "config/s3_conf.yaml"
    out = "out/s3"
    input_data = load_yaml(input)
    behaviour = load_yaml(config)
    st.set_page_config("INCIT-EV Paper")
    toc = Toc()
    toc.placeholder(sidebar=True)
    st.title("INCIT-EV")
    fig = plot_cache(input_data, behaviour)
    st.pyplot(fig)
    impact_confidence = pd.read_csv(os.path.join(out, "impact_kw_confidence_5000it_7d.csv"))
    impact_mean = pd.read_csv(os.path.join(out, "impact_kw_mean_5000it_7d.csv"))
