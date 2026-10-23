import numpy as np
import pandas as pd
import xarray

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

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


import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


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
