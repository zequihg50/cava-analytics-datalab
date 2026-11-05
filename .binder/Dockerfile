FROM zequihg50/cava-datalab:20261106

COPY --chown=jovyan:users ../main.ipynb ../ne_110m_admin_0_countries.geojson ../README.md ../temp-and-precip-indicators-python.ipynb ../utils.py /home/jovyan/

EXPOSE 8888

CMD ["micromamba", "run", "-n", "base", "jupyter", "lab", \
     "--ip=0.0.0.0", "--port=8888", "--no-browser"]
