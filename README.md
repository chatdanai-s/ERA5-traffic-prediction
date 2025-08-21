# ERA5-traffic-prediction
Traffic Volume Prediction Using Atmospheric Reanalysis Data (ERA5 hourly data)

This project aims to forecase traffic volume sourced from Metro Interstate Traffic Volume Data (https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume) using atmospheric reanalysis data from ERA5 hourly data on single levels from 1940 to present (https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels). Moreover, because the traffic volume dataset also contains qualitative local weather observations, a model based on these descriptions are also compared against the descriptions present in the ERA5 data.

The regression methods used in this project include linear regression, decision tree, random forest, bagging, and XGBoost. All the models are compared against each other using R^2 and RMSE metrics.
