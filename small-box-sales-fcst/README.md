# Small Box Retail Sales Forecasting

This is an ongoing project to predict weekly sales for a local boutique retailer using
supervised machine learning.

### Contents:

[Data Wrangling:](./data-wrangling)

A collection of Python modules to acquire and clean the data used for sales forecasting. The list of sources currently includes:

* Square - daily sales data
* Facebook - Social media activity in an attempt to model customer traffic
* Dark Sky - Weather for the store's location

[EDA:](./eda)

A set of Jupyter Notebooks with graphical and numerical exploration of the data acquired above. In addition to simple line plots of sales data, there's also things like feature correlation and partial autocorrelation of the weekly sales data.

[Data:](./data)

Raw data used to forecast.

[Models](./models)

A collection of Jupyter Notebooks and Python modules to generate the forecast.  The Python modules implment some needed utilities like lag generation and walk-forward testing. There are 5 Notebooks and each explores a different regression algorithm for forecasting sales.

[Baseline](./models/baseline.ipynb)

A baseline, non-ML forecast using a really simple method that the non-technical store owners typically employ.

[Linear Models](./models/linear-models.ipynb)

Explore the performance of a suite of linear models (linear regression, ridge, lasso, elastic net).

[XGboost](./models/xgboost.ipynb)

Explore a tree-based algorithm for sales forecasting. It works suprisingly well on this small amount of data but requires lots more tuning. Helpful that you can easily see the most important features in generating a forecast.

[Seasonal ARIMA](./models/sarima.ipynb)

For sake of completeness, try an ARIMA model.

[Facebook Prophet](./models/prophet.ipynb)

Try Prophet on this small data set. It did what it was designed to do in delivering a respectable forecast with very little tuning out of the box. There are some tricks in back testing that require reading through code to unravel.

### Summary of Results:

| Model             | RMSE   | MAPE   |
| ----------------- | ------ | ------ |
| Baseline          | 596.27 | 25.37% |
| Linear Regression | 453.54 | 20.64% |
| Ridge (alpha=0.1) | 453.82 | 20.33% |
| Lasso (alpha=0.1) | 453.70 | 20.56% |
| ElasticNet        | 452.84 | 19.66% |
| XGBoost           | 461.37 | 19.51% |
| SARIMA            | N/A    | N/A    |
| Facebook Prophet  | 572.01 | 36.57% |

The above results were generated using walk forward testing of the models. The walk started with a minimum training set (about 4 months of data). For each step, the model is trained, 7 days are forecasted and compared against actual sales using the above metrics. The training set is then expanded by a week and a new weekly forecast is generated. This process was repeated for about 30 steps to give a good overall sense of model performance. The values above are the average over all steps.

### Next Steps:


