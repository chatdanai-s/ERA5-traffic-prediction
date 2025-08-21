# ERA5-traffic-prediction
Traffic Volume Prediction Using Atmospheric Reanalysis Data (ERA5 hourly data)

This project aims to forecast traffic volume sourced from Metro Interstate Traffic Volume Data (https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume) using atmospheric reanalysis data from ERA5 hourly data on single levels from 1940 to present (https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels).

Moreover, because the traffic volume dataset also contains qualitative local weather observations, a model based on these descriptions are also compared against the descriptions present in the ERA5 data.

The regression methods used in this project include linear regression, decision tree, random forest, bagging, and XGBoost. All the models are compared against each other using R^2 and RMSE metrics.

The files in this repository include
* ERA5 data (raw): Raw ERA5 data requested from the website in GRIB format
* ERA5 data (csv): ERA5 data converted to workable CSV via grib2csv.py
* unused data: Other traffic datasets which was acquired, but ultimately unused in this project
* Results: Model results from models utilizing ERA5 weather descriptions, Metro Interstate detailed weather descriptions, Metro Interstate overall weather descriptions, and no weather descriptions included
* ERA5_API_DL.py: An attempt to acquire the GRIB files using API requests. Due to the size of the requests, it was ultimately decided to directly request the data from the website.
* project.ipynb: The project. Contains all data exploration, feature engineering, and model deployment code.
* report.pdf: A written pdf report on the project.
* slides.pdf: A PowerPoint slide presentation on the project. 
