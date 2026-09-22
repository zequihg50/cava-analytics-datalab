import numpy as np
import pandas as pd
import xarray

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

import cavapy
from cavapy.data import load_era5, load_cordex_core

def plot_annual_mean_and_trend(results, mask, settings, indices, columns, titles, extent):
    fig, axes = plt.subplots(
        nrows=len(indices),
        ncols=2,
        figsize=(10, 7),
        subplot_kw={"projection": ccrs.PlateCarree()},
        layout="constrained",
    )
    
    for i, idx in enumerate(indices):
        for j, col in enumerate(columns):
            ax = axes[i, j]
    
            data = results[f"{idx}_{col}"].where(mask)
            s = settings[idx][col]
            data.plot(
                ax=ax,
                transform=ccrs.PlateCarree(),
                cmap=s["cmap"], vmin=s["vmin"], vmax=s["vmax"],
                add_colorbar=True,
                cbar_kwargs={
                    #"shrink": 0.75, "label": ("Annual precipitation\n(mm)" if idx == "prcptot" and col == "mean" else "Days/year" if idx in ["dd", "r20"] and col == "mean" else "Trend (units/year)"),
                    "shrink": 0.75, "label": data.attrs["units"],
                })
    
            # Overlay significant grid cells on the trend column
            if col == "trend":
                pvalue = results[f"{idx}_pvalue"].where(mask)
                significant = pvalue < 0.05
    
                lon, lat = xarray.broadcast(data.longitude, data.latitude)
                ax.scatter(lon.where(significant),lat.where(significant),
                    s=2, color="black", linewidths=0, transform=ccrs.PlateCarree())
    
            ax.coastlines()
            ax.add_feature(cfeature.BORDERS, linewidth=1, edgecolor="black")
            ax.set_extent(extent, crs=ccrs.PlateCarree())
            if i == 0:
                ax.set_title(titles[j], fontsize=12)
            if j == 0:
                ax.text(-0.08, 0.5, idx.upper(), transform=ax.transAxes, rotation=90,
                        va="center", ha="center", fontsize=13, fontweight="bold")
    
    return fig, axes


def plot_biases(
    indices,
    mask,
    min_lon,
    max_lon,
    min_lat,
    max_lat,
    figsize_per_model=4,
    figsize_per_row=2,
    spacer_height=0.35,
    hspace=0.15,
    wspace=0.08,
    border_linewidth=1,
    colorbar_shrink=0.8,
):
    """
    Plot multiple climate indices in a grid of maps.

    Parameters
    ----------
    indices : list of tuples
        Each tuple contains:
        (data_array, name, vmin, vmax, cmap)

        Each data array must have 'source' and 'model' dimensions.

    mask : xarray.DataArray or compatible object
        Boolean mask applied to each data array.

    min_lon, max_lon, min_lat, max_lat : float
        Geographic extent of the maps.

    figsize_per_model : float, default=4
        Figure width per model column.

    figsize_per_row : float, default=2
        Figure height per source row.

    spacer_height : float, default=0.35
        Relative height of the spacer between consecutive indices.

    hspace, wspace : float
        Vertical and horizontal subplot spacing.

    border_linewidth : float
        Width of country borders.

    colorbar_shrink : float
        Shrink factor for each index's colorbar.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The generated figure.

    axs : dict
        Axes indexed by (index_number, source_number, model_number).
        Spacer rows do not have axes.
    """

    if not indices:
        raise ValueError("indices must contain at least one index.")

    # Use the first index to establish the grid.
    reference_da = indices[0][0]
    sources = reference_da["source"].values
    models = reference_da["model"].values

    n_sources = len(sources)
    n_models = len(models)
    n_indices = len(indices)

    if n_sources == 0 or n_models == 0:
        raise ValueError("The source and model dimensions must not be empty.")

    # Build the grid, including spacer rows between indices.
    height_ratios = []

    for i in range(n_indices):
        height_ratios.extend([1] * n_sources)

        if i < n_indices - 1:
            height_ratios.append(spacer_height)

    fig = plt.figure(
        figsize=(
            figsize_per_model * n_models,
            figsize_per_row * sum(height_ratios),
        )
    )

    gs = fig.add_gridspec(
        len(height_ratios),
        n_models,
        height_ratios=height_ratios,
        hspace=hspace,
        wspace=wspace,
    )

    # Create the map axes and skip the spacer rows.
    axs = {}
    row = 0

    for i in range(n_indices):
        for j in range(n_sources):
            for k in range(n_models):
                axs[(i, j, k)] = fig.add_subplot(
                    gs[row, k],
                    projection=ccrs.PlateCarree(
                        central_longitude=0
                    ),
                )

            row += 1

        if i < n_indices - 1:
            row += 1

    # Plot each index for every source/model combination.
    for i, (da, name, vmin, vmax, cmap) in enumerate(indices):

        for j, source in enumerate(sources):
            for k, model in enumerate(models):

                ax = axs[(i, j, k)]

                da.sel(
                    source=source,
                    model=model,
                ).where(mask).plot(
                    ax=ax,
                    transform=ccrs.PlateCarree(),
                    vmin=vmin,
                    vmax=vmax,
                    cmap=cmap,
                    add_colorbar=False,
                )

                ax.coastlines()

                ax.add_feature(
                    cfeature.BORDERS,
                    linewidth=border_linewidth,
                    edgecolor="black",
                )

                ax.set_extent(
                    (min_lon, max_lon, min_lat, max_lat),
                    crs=ccrs.PlateCarree(),
                )

                # Preserve the original title behavior.
                if j % 2 == 0:
                    ax.set_title(
                        "-".join(str(model).split("-")[1:])
                    )
                else:
                    ax.set_title(None)

                if k == 0:
                    ax.set_ylabel(f"{name}\n{source}")

        # One shared colorbar per index.
        axes_group = [
            axs[(i, j, k)]
            for j in range(n_sources)
            for k in range(n_models)
        ]

        fig.colorbar(
            axs[(i, 0, 0)].collections[0],
            ax=axes_group,
            shrink=colorbar_shrink,
            label=name,
        )

    return fig, axs

def load_scenarios(df, vs, domain, scenarios, periods, lat_lim, lon_lim):
    min_lat, max_lat = lat_lim
    min_lon, max_lon = lon_lim

    for scenario in scenarios:
        for period in periods:
            subset = df[(df["location"].str.contains(domain)) & (df["location"].str.contains(f'/{scenario}/')) & (df["location"].str.contains('/interp025bc/'))]
            ds = load_cordex_core(subset , vs, period, (max_lat, min_lat), (min_lon, max_lon))
            if not (period[1][:4] == "2100"):
                ds = ds.isel(time=slice(None, -1))

            if "tasmin" in vs and "tasmax" in vs and "pr" in vs:
                result = xarray.merge([
                    cavapy.indices.prcptot(ds["pr"] * 86400).rename("prcptot"),
                    cavapy.indices.dd(ds["pr"] * 86400).rename("dd"),
                    cavapy.indices.cdd(ds["pr"] * 86400).rename("cdd"),
                    cavapy.indices.cwd(ds["pr"] * 86400).rename("cwd"),
                    cavapy.indices.r20(ds["pr"] * 86400).rename("r20"),
                    cavapy.indices.su(ds["tasmax"] - 273.15).rename("su"),
                    cavapy.indices.tr(ds["tasmin"] - 273.15).rename("tr"),
                    cavapy.indices.hwvs(ds["tasmax"] - 273.15).rename("hwvs")])
            elif "pr" in vs:
                result = xarray.merge([
                    cavapy.indices.prcptot(ds["pr"] * 86400).rename("prcptot"),
                    cavapy.indices.dd(ds["pr"] * 86400).rename("dd"),
                    cavapy.indices.cdd(ds["pr"] * 86400).rename("cdd"),
                    cavapy.indices.cwd(ds["pr"] * 86400).rename("cwd"),
                    cavapy.indices.r20(ds["pr"] * 86400).rename("r20")])
            elif "tasmin" in vs and "tasmax" in vs:
                result = xarray.merge([
                    cavapy.indices.su(ds["tasmax"] - 273.15).rename("su"),
                    cavapy.indices.tr(ds["tasmin"] - 273.15).rename("tr"),
                    cavapy.indices.hwvs(ds["tasmax"] - 273.15).rename("hwvs")])
            else:
                raise ValueError(f"Wrong combination of variables {vs}.")

            yield scenario, period, result

def plot_scenarios(
    df, v, domain, hist, scenarios, periods,
    lat_lim, lon_lim, mask,
    figsize_per_model=4, figsize_per_row=2, spacer_height=0.35,
    hspace=0.15, wspace=0.08, border_linewidth=1, colorbar_shrink=0.8
):
    min_lat, max_lat = lat_lim
    min_lon, max_lon = lon_lim

    if v == "pr":
        vs, n_indices = ["pr"], 5
    elif v == "temp":
        vs, n_indices = ["tasmin", "tasmax"], 3
    else:
        vs, n_indices = ["pr", "tasmin", "tasmax"], 8
    
    n_sources, n_models = len(scenarios), len(periods)

    # Build the grid, including spacer rows between indices.
    height_ratios = []
    for i in range(n_indices):
        height_ratios.extend([1] * n_sources)
        if i < n_indices - 1:
            height_ratios.append(spacer_height)

    fig = plt.figure(figsize=(figsize_per_model * n_models, figsize_per_row * sum(height_ratios)))
    gs = fig.add_gridspec(len(height_ratios), n_models, height_ratios=height_ratios, hspace=hspace, wspace=wspace)
    axs, row = {}, 0
    for i in range(n_indices):
        for j in range(n_sources):
            for k in range(n_models):
                axs[(i, j, k)] = fig.add_subplot(gs[row, k], projection=ccrs.PlateCarree(central_longitude=0))
            row += 1
        if i < n_indices - 1:
            row += 1

    # begin actual plot
    settings = {
        "prcptot": {"vmin": -160, "vmax": 160, "cmap": "BrBG"},
        "dd":     {"vmin": -25, "vmax": 25, "cmap": "BrBG_r"},
        "cdd":    {"vmin": -30, "vmax": 30, "cmap": "BrBG_r"},
        "cwd":    {"vmin": -8, "vmax": 8, "cmap": "BrBG"},
        "r20":    {"vmin": -3, "vmax": 3, "cmap": "BrBG"},
        "su":     {"vmin": -200, "vmax": 200, "cmap": "RdBu_r"},
        "tr":     {"vmin": -250, "vmax": 250, "cmap": "RdBu_r"},
        "hwvs":   {"vmin": -10, "vmax": 10, "cmap": "RdBu_r"},
    }

    for s, period, ds in load_scenarios(df, vs, domain, scenarios, periods, lat_lim, lon_lim):
        bias = (ds.mean(["model", "time"]) - hist.mean(["model", "time"])).where(mask)
        change = ds.mean("time") - hist.mean("time")
        n_positive = (change > 0).sum(dim="model")
        n_negative = (change < 0).sum(dim="model")
        agreement = ((n_positive >= 5) | (n_negative >= 5))
        
        for k in range(n_indices):
            i = scenarios.index(s)
            j = periods.index(period)
            ax = axs[(k, i, j)]
            vname = list(ds.data_vars)[k]

            bias[vname].plot(ax=ax, transform=ccrs.PlateCarree(), add_colorbar=False, **settings[vname])
            agree = agreement[vname]
            valid = agree & mask
            lon, lat = xarray.broadcast(agree.longitude, agree.latitude)
            ax.scatter(lon.where(valid),lat.where(valid), s=2, color="black", linewidths=0, transform=ccrs.PlateCarree())
            
            ax.coastlines()
            ax.add_feature(cfeature.BORDERS, linewidth=border_linewidth, edgecolor="black")
            ax.set_extent((min_lon, max_lon, min_lat, max_lat), crs=ccrs.PlateCarree())

            # Preserve the original title behavior.
            if (i % 2 == 0):
                ax.set_title("-".join([p[:4] for p in period]), fontsize=7.5)
            else:
                ax.set_title(None)
            if j == 0 and i == 0:
                ax.text(-0.08, -0.125, vname.upper(), transform=ax.transAxes, rotation=90,
                        va="center", ha="center", fontsize=10, fontweight="bold")

            # if k == 0:
            #     ax.set_ylabel(f"{name}\n{source}")

    for k in range(n_indices):
        axes_group = [axs[(k, i, j)] for i in range(n_sources) for j in range(n_models)]
        fig.colorbar(axs[(k, 0, 0)].collections[0], ax=axes_group, shrink=colorbar_shrink, label="")

    return fig, axs
