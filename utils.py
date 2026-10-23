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