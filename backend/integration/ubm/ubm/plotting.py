import os

import numpy as np
from matplotlib import pyplot as plt
from shapely.geometry import MultiPolygon


def plot_shape_raster(square_geometry, zone_geometry):
    """
    Debugging function to plot the square of ENACT POP, together with the zone of interest.

    Parameters
    ----------
    square_geometry: Polygon or MultiPolygon
        Polygon of ENACT-POP
    zone_geometry: Polygon or MultiPolygon
        Polygon of the zone

    """
    ax = plt.gca()
    x, y = square_geometry.exterior.xy
    ax.plot(x, y, color="green")
    x, y = zone_geometry.exterior.xy
    ax.plot(x, y, color="red")
    plt.show()


def plot_shape_enact_corine_raster(zone_geometry, enact_geometry, corine_geometry, i_1, i_2):
    """
    Debugging function to plot the squares of ENACT POP and Corine, together with the zone of interest and a set of
    intersections

    Parameters
    ----------
    zone_geometry: Polygon or MultiPolygon
        Polygon of the zone
    enact_geometry: Polygon or MultiPolygon
        Polygon of ENACT-POP
    corine_geometry: Polygon or MultiPolygon
        Polygon of Corine Land Use
    i_1: Polygon or MultiPolygon
        Polygon of Intersection between ENACT-POP and Corine Squares
    i_2: Polygon or MultiPolygon
        Polygon of intersection among ENACT-POP, Corine and the Zone shape

    """
    for p, c, l in zip([zone_geometry, enact_geometry, corine_geometry, i_1, i_2],
                       ["m-", "b-", "r-", "g--", "b--"],
                       ["Zone", "Enact", "Corine", "I Corine-Enact", "I Corine-Enact-Shape"]):
        ax = plt.gca()
        if isinstance(p, MultiPolygon):
            for poly in list(p):
                x, y = poly.exterior.xy
                ax.plot(x, y, c, label=l)
        else:
            if p.is_empty:
                continue
            x, y = p.exterior.xy
            ax.plot(x, y, c, label=l)
    plt.legend()
    plt.show()


def get_range(max: np.ndarray):
    """
    Helper function to plot the maximum on the matplotlib plot.

    Parameters
    ----------
    max: np.ndarray
        Max values of the Map

    Returns
    -------
    tick: float
        tick to use as max in the plot

    """
    for i in range(0, 10):
        one = 1 * 10 ** i
        two = 2 * 10 ** i
        five = 5 * 10 ** i
        if max / one < 8:
            return one
        if max / two < 8:
            return two
        if max / five < 8:
            return five
    return 1 * 10 ** 10


def plot_day_night(gdf, vehicle_type: str = "Vehicles", day_column="day_parking_plot",
                   night_column="night_parking_plot"):
    """
    Plot Day and Night Data of the GeoDataFrame.

    Parameters
    ----------
    gdf: GeoDataFrame
        GeoDataFrame augmented with car parked data.
    vehicle_type: str
        Type of vehicle to use in the title of the plot.
    day_column: str
        Name of the column to use as Day
    night_column: str
        Name of the column to use as Night

    """
    os.makedirs('./img', exist_ok=True)
    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(20, 10), dpi=1500)
    max_map = np.around(gdf[day_column].max(), 0) if gdf[day_column].max() > gdf[night_column].max() else np.around(
        gdf[night_column].max(), 0)
    ranges = get_range(max_map)
    ticks = np.append(np.arange(0, int(max_map), ranges), max_map)
    gdf.plot(column=day_column, legend=True, cmap=plt.get_cmap('Oranges'), vmax=max_map, vmin=0,
                  edgecolor='#862a04',
                  linewidth=0.2, ax=ax0, legend_kwds={'ticks': ticks})
    ax0.axis("off")
    ax0.title.set_text("Day Parking - " + vehicle_type)
    plt.xticks(ticks=[], labels=[])
    plt.yticks(ticks=[], labels=[])
    plt.tight_layout()
    plt.savefig(f"{day_column}.png", dpi=900)
    plt.show()
    gdf.plot(column=night_column, legend=True, vmax=max_map, vmin=0, cmap=plt.get_cmap('Blues'),
                  edgecolor='#083471', ax=ax1,
                  linewidth=0.2, legend_kwds={'ticks': ticks})
    ax1.axis("off")
    ax1.title.set_text("Night Parking - " + vehicle_type)
    plt.xticks(ticks=[], labels=[])
    plt.yticks(ticks=[], labels=[])
    plt.tight_layout()
    plt.savefig(f"img/{night_column}.png", dpi=900)
    plt.show()
    return fig


def plot_column(gdf, title: str = "Error", column="error", cmap='Oranges', edgecolor='#862a04'):
    """
    Plot a column of the GeoDataFrame.

    Parameters
    ----------
    gdf: GeoDataFrame
        GeoDataFrame augmented with car parked data.
    title: str
        Title of the Plot
    column: str
        Title of the column
    cmap: str
        Cmap of the matplotlib
    edgecolor: str
        Color of the shapes edges

    """
    fig, ax = plt.subplots(1, 1)
    plt.title(title)
    max_map = gdf[column].max()
    ax = gdf.plot(column=column, legend=True, cmap=plt.get_cmap(cmap), vmax=max_map, vmin=0,
                  edgecolor=edgecolor,
                  linewidth=0.2, ax=ax)
    ax.axis("off")
    plt.xticks(ticks=[], labels=[])
    plt.yticks(ticks=[], labels=[])
    plt.tight_layout()
    plt.savefig(f"img/{column}.png", dpi=900)
    plt.show()
