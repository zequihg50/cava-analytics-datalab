[![Binder](https://mybinder.org/badge_logo.svg)](https://gesis.mybinder.org/v2/gh/zequihg50/cava-analytics-datalab/HEAD?urlpath=%2Fdoc%2Ftree%2Fmain.ipynb) [![IFCA (CSIC-UC)](https://img.shields.io/badge/launch-IFCA-orange)](https://hub.climate.ifca.es/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Fzequihg50%2Fcava-analytics-datalab&urlpath=lab%2Ftree%2Fcava-analytics-datalab%2Fmain.ipynb&branch=main)

# CAVA Analytics Datalab

The CAVA Analytics Datalab brings the CAVA ecosystem together in a ready-to-use cloud environment that can be deployed with a single click. It provides the computing infrastructure needed to access and process climate data directly, without requiring users to download or manage large datasets locally.

With [CAVAanalytics](https://github.com/un-fao/CAVAanalytics) and [cavapy](https://github.com/un-fao/cavapy) pre-installed and ready to use, users can run workflows, perform climate impact assessments, and generate visualizations with just a few clicks.

## Running in Binder

You can launch interactive, browser-based code environments for free using [binder](https://mybinder.org). Use the Binder launcher available at the top of this document.

What MyBinder does:

- Interactive Code: Turns public Git repositories (such as GitHub or GitLab) into live, executable Jupyter notebooks and scripts.
- No Local Setup: Lets users run Python, R, Julia, and other scientific tools directly in a web browser without installing software.
- Free and Open-Source: Runs as a non-profit, community-managed public service powered by BinderHub and Kubernetes.

## Running in Docker

Run the CAVA Analytics Datalab in any machine of your own using the publicly available Docker image:

```bash
docker pull zequihg50/cava-datalab:20261102
docker run -n cava-datalab -p 8888:8888 zequihg50/cava-datalab:20261102
```

The URL of your JupyterLab instance will be displayed on the terminal, copy/paste it in the web browser and enjoy!

# References

- CAVA platform - https://cavaplatform.fao.org
- CAVAanalytics - https://un-fao.github.io/CAVAanalytics/
