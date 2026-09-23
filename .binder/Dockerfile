FROM jupyter/base-notebook:latest

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

USER root
RUN apt-get update && apt-get install -y xorg git wget build-essential tzdata && apt-get clean && chown -R $NB_USER:users /home/$NB_USER

USER jovyan
RUN conda install mamba -y -n base -c conda-forge && \
    # https://github.com/proxystore/taps/issues/151#issuecomment-2340406425 \
    mamba install -y -n base jupyter 'libsqlite<3.46' nbgitpuller jupyterlab-git

RUN conda create -n cavapy && \
    source /opt/conda/bin/activate cavapy && \
    mamba install -y jupyter xarray pandas geopandas shapely matplotlib cartopy netcdf4 cftime dask iris zarr fsspec s3fs h5py gcsfs siphon beautifulsoup4 scikit-learn h5netcdf python-swiftclient \
    nco cdo && \
    python -m ipykernel install --name cavapy --display-name "cavapy" --prefix /opt/conda
