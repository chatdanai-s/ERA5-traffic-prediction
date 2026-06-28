# ERA5 Traffic Volume Prediction

Hourly traffic volume prediction on Minneapolis I-94 using atmospheric reanalysis data (ERA5) as an alternative to local weather station observations. Five regression models are benchmarked across four weather feature sets, including a comparison between directly observed weather and gridded ERA5 climate data.

**Datasets**
- [Metro Interstate Traffic Volume](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume) -- hourly traffic counts on I-94, 2012-2018
- [ERA5 Hourly Data on Single Levels](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels) -- gridded atmospheric reanalysis, requested year-by-year

**Models:** Linear Regression, Decision Tree, Random Forest, Bagging, XGBoost

**Evaluation:** R², RMSE (train), RMSE (test), RMSE (bad weather only)

---

## Repository Structure

```
ERA5-traffic-prediction/
├── ERA5 data (raw)/           # Raw GRIB files from Copernicus CDS
├── ERA5 data (csv)/           # GRIB converted to CSV via grib2csv.py
├── cleaned data/              # Processed outputs from EDA notebook
├── Results/                   # Model evaluation CSVs per feature set
├── unused data/               # Other traffic datasets not used
├── grib2csv.py                # GRIB-to-CSV conversion script
├── ERA5_API_DL.py             # Attempted API download (abandoned due to request size)
├── 01_EDA_and_feature_engineering.ipynb
├── 02_data_modelling.ipynb
├── report.pdf
└── slides.pdf
```

---

## Data Pipeline

### 1. Data Collection

ERA5 data was requested year-by-year from the Copernicus Climate Data Store in GRIB format, then converted to CSV using a custom `grib2csv.py` script. ERA5 coordinates were fixed to the MN DoT ATR Station 301 (Route I-94, Reference Post 239+00.922), located using the [Roadway Project Mapping Application](https://www.dot.state.mn.us/roadway/data/rpma.html).

An API-based download (`ERA5_API_DL.py`) was attempted but abandoned due to request size limitations.

### 2. Data Cleaning

**Traffic dataset (48,176 rows after cleaning)**
- Removed 17 duplicate rows.
- Removed rows with temperature below 200 K (physically impossible; measurement error).
- Removed one row with rainfall exceeding 8,000 mm (instrument error).
- Filled `holiday` NaN values with `'None'` to denote non-holiday hours.
- Standardised inconsistent capitalisation in `weather_description` (e.g. `'Sky is Clear'` -> `'sky is clear'`).

**ERA5 dataset**
- Seven annual CSV files (2012-2018) concatenated into one dataframe.
- Columns retained: 2m temperature (`t2m`), total/low/medium/high cloud cover (`tcc`, `lcc`, `mcc`, `hcc`), precipitation type (`ptype`), total precipitation (`tp`), snowfall (`sf`), convective precipitation (`cp`), large-scale precipitation (`lsp`).

### 3. Feature Engineering

**Cyclic time encoding**
Hour of day, day of week, and month of year are encoded using 5-harmonic sin/cos decomposition rather than one-hot encoding. This preserves the cyclic nature of these features and reduces dimensionality from 43 columns (24+7+12) down to 30 (5x2x3).

**One-hot encoding**
- `holiday`: 11 binary columns (one per named US holiday; `None` dropped)
- `weather_main`: 11 binary columns (main weather categories)
- `weather_description`: 37 binary columns (detailed weather descriptions)
- ERA5 precipitation type: precipitation type combined with a 0.1 mm threshold, producing light/heavy variants per type (e.g. `Rain_light`, `Rain_heavy`)

---

## EDA Insights

![Traffic volume distribution](images/cell-17-0.png)

### Time Patterns

Traffic volume is strongly driven by time of day and day of week. The boxplots below show the distributions by hour, weekday, and month.

![Traffic volume by hour](images/cell-45-0.png)
![Traffic volume by day of week](images/cell-48-0.png)
![Traffic volume by month](images/cell-46-0.png)

**Peak vs off-peak hours** (defined as 06:00-09:00 and 15:00-18:00 vs 10:00-15:00):

| Period | Median traffic volume |
|---|---|
| Peak hours | 5,181 |
| Off-peak hours | 4,739 |
| Nighttime | 1,117 |

Peak hours carry 9.3% more traffic than off-peak hours. Nighttime volume drops to less than a quarter of peak levels.

![Median traffic by hour](images/cell-57-1.png)

**Weekday vs weekend:** Weekend traffic is 34.7% lower than weekdays (median 2,675 vs 4,094).

![Weekday vs weekend traffic](images/cell-61-1.png)

**Year-on-year growth:** No sustained growth or decline trend over 2012-2018. The median annual growth rate across years is 0.36%, with fluctuations between -3.7% and +8.3%.

![Year-on-year traffic growth](images/cell-59-1.png)

### Weather Effects

**Holidays** reduce traffic by 76.0% overall on weekdays. The reduction is consistent across all weekdays (ranging from -69.9% on Tuesdays to -81.4% on Thursdays). No holiday observations fall on weekends.

![Holiday vs non-holiday traffic by day of week](images/cell-55-1.png)

**Bad weather** (any `weather_main` value other than `Clear` or `Clouds`) reduces overall median traffic by 11.7%. The effect is strongest late at night (hours 20:00-23:00, -6% to -9%) and weakest in the early morning hours 04:00-05:00, where traffic is marginally higher in bad weather.

![Bad weather vs good weather traffic by hour](images/cell-53-1.png)

**Weather type** (both main and detailed) has a visible impact on traffic volume. More granular descriptions show greater variation in traffic across conditions.

![Traffic volume by main weather type](images/cell-28-0.png)
![Traffic volume by detailed weather description](images/cell-29-0.png)

### ERA5 vs Observed Data Comparison

Temperature shows strong agreement between ERA5 and observed station data, confirming geographic alignment. Cloud cover and precipitation show poor agreement, attributed to ERA5 being a gridded model average rather than a point observation, and suspected measurement gaps in the station's precipitation records.

![Temperature correlation: ERA5 vs observed](images/cell-78-0.png)
![Cloud cover correlation: ERA5 vs observed](images/cell-79-0.png)
![Precipitation correlation: ERA5 vs observed](images/cell-80-0.png)

Despite weak correlation between raw precipitation values across the two sources, partitioning ERA5 precipitation by type and a 0.1 mm threshold reveals a clear difference in traffic volume distributions -- heavier precipitation events correspond to meaningfully lower traffic.

![Traffic volume by ERA5 precipitation type](images/cell-89-0.png)

---

## Modelling

### Feature Sets

Four feature sets are evaluated to isolate the contribution of each weather data source:

| Feature set | Weather features included | Total columns |
|---|---|---|
| No weather | None (time + temperature + holidays only) | 42 |
| Main weather | `weather_main` (11 categories) | 53 |
| Descriptive weather | `weather_description` (37 categories) | 79 |
| ERA5 weather | ERA5 precipitation type x threshold (16 columns) | 56 |

All feature sets include: temperature, 30 harmonic seasonality columns (hour/day/month), and 11 holiday indicator columns.

### Model Hyperparameters

All tree-based models are regularised to reduce overfitting observed in initial runs.

| Model | Key hyperparameters |
|---|---|
| Linear Regression | Default (no tuning required) |
| Decision Tree | `max_depth=8`, `min_samples_split=40`, `min_samples_leaf=20` |
| Random Forest | `n_estimators=100`, `max_depth=8`, `min_samples_split=40`, `max_features='sqrt'` |
| Bagging | `n_estimators=100`, `max_samples=0.5`, `max_features=0.5`, `bootstrap_features=True` |
| XGBoost | `max_depth=4`, `min_child_weight=50`, `subsample=0.5`, `reg_alpha=10`, `reg_lambda=10`, `gamma=2` |

The test set is the last 30% of rows in chronological order, simulating future prediction rather than interpolation.

---

## Results

### Model Comparison Across Feature Sets

![RMSE and R2 by model and feature set](images/cell-33-0.png)

Full numerical results across all 20 model-feature combinations:

**No weather features**

| Model | R² | Train RMSE | Test RMSE | Bad Weather RMSE |
|---|---|---|---|---|
| Linear Regression | 0.831 | 812.0 | 812.2 | 866.6 |
| Decision Tree | 0.937 | 464.8 | 493.9 | 553.0 |
| Random Forest | 0.936 | 500.0 | 501.1 | 551.8 |
| Bagging | 0.937 | 493.6 | 496.0 | 543.8 |
| XGBoost | 0.947 | 375.5 | 454.8 | 517.9 |

**Main weather features (`weather_main`)**

| Model | R² | Train RMSE | Test RMSE | Bad Weather RMSE |
|---|---|---|---|---|
| Linear Regression | 0.832 | 809.5 | 810.1 | 864.8 |
| Decision Tree | 0.937 | 464.8 | 494.0 | 553.1 |
| Random Forest | 0.923 | 547.7 | 547.2 | 591.2 |
| Bagging | 0.936 | 498.1 | 500.1 | 545.4 |
| XGBoost | 0.948 | 374.8 | 450.0 | 511.9 |

**Descriptive weather features (`weather_description`)**

| Model | R² | Train RMSE | Test RMSE | Bad Weather RMSE |
|---|---|---|---|---|
| Linear Regression | 0.832 | 809.6 | 809.9 | 863.8 |
| Decision Tree | 0.937 | 463.4 | 494.1 | 553.8 |
| Random Forest | 0.935 | 499.9 | 501.3 | 549.5 |
| Bagging | 0.936 | 492.4 | 495.9 | 541.3 |
| XGBoost | 0.948 | 375.0 | 450.5 | 512.0 |

**ERA5 weather features**

| Model | R² | Train RMSE | Test RMSE | Bad Weather RMSE |
|---|---|---|---|---|
| Linear Regression | 0.837 | 804.2 | 798.4 | 840.6 |
| Decision Tree | 0.940 | 463.6 | 483.5 | 529.3 |
| Random Forest | 0.935 | 505.3 | 503.6 | 550.2 |
| Bagging | 0.937 | 495.6 | 497.1 | 541.2 |
| XGBoost | 0.952 | 362.2 | 432.6 | 476.1 |

### Actual vs Predicted Traffic Volume

![Actual vs predicted traffic volume per model and feature set](images/cell-35-0.png)

### Key Takeaways

**XGBoost with ERA5 features is the best-performing configuration** across all metrics: R² = 0.952, test RMSE = 432.6, bad weather RMSE = 476.1. This is the only configuration that breaks below 433 on test RMSE and below 477 on bad weather RMSE.

**ERA5 weather features consistently outperform observed weather features**, particularly on bad weather RMSE -- the margin where weather quality matters most. The Decision Tree with ERA5 improves bad weather RMSE by 24 units over its no-weather baseline, while the same model using descriptive station weather sees no meaningful gain.

**Adding observed weather descriptions (main or detailed) provides minimal benefit** over using no weather at all. For most models, the RMSE difference between the no-weather and descriptive-weather feature sets is under 5 units, suggesting the station weather data adds little predictive signal beyond what time and holiday features already capture.

**Time and holiday features dominate predictive power.** Even the no-weather XGBoost achieves R² = 0.947, close to the best result of 0.952. The biggest performance gap is between linear regression and all tree-based models, reflecting strong nonlinear interactions between time-of-day and traffic patterns.

**Linear regression substantially underperforms** across all feature sets (R² around 0.83, RMSE ~800), indicating the time-traffic relationship is not well captured by a linear model.

---

## Stack

- [pandas](https://pandas.pydata.org) -- data wrangling
- [NumPy](https://numpy.org) -- numerical operations and harmonic encoding
- [scikit-learn](https://scikit-learn.org) -- Linear Regression, Decision Tree, Random Forest, Bagging
- [XGBoost](https://xgboost.readthedocs.io) -- gradient boosted trees
- [Matplotlib](https://matplotlib.org) / [Seaborn](https://seaborn.pydata.org) -- visualisation
- [cfgrib](https://github.com/ecmwf/cfgrib) -- GRIB file reading (via `grib2csv.py`)
