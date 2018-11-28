"""
linreg
~~~~~~~~~~~~~~~~
Learning exercise by implementing Linear Regression, Gradient Descent and R^2
"""
from __future__ import print_function

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def linear_regression(x, y, alpha, steps=1000):
    """ Simple implementation of gradient descent to find values for
    m and x that minimize Mean Squared Error"""
    m = 0.0
    b = 0.0
    n = float(len(x))
    errors = []

    for steps in range(steps):
        y_hat = m * x + b

        error = y - y_hat
        mse = np.sum(error**2) / n
        errors.append(mse)

        m_gradient = -(2 / n) * np.sum(error * x)
        b_gradient = -(2 / n) * np.sum(error)

        m = m - (alpha * m_gradient)
        b = b - (alpha * b_gradient)

        if steps % 10 == 0:
            print('MSE @ {} = {:.4f}'.format(steps, mse))

    return m, b, errors


def r_squared(y, y_hat):
    """ Simple implementation of the Coefficient of Determination - R^2
    """
    fit_var = ((y - y_hat)**2).sum()
    y_mean = np.mean(y)
    mean_var = ((y - y_mean)**2).sum()
    return 1 - (fit_var / mean_var)


def main():
    # Read train & test data from CSV files
    df = pd.read_csv('train.csv')
    df_train = df.dropna()
    df = pd.read_csv('test.csv')
    df_test = df.dropna()

    slice_size = 500

    # Slice train and test X and y(s) as numpy arrays
    x_train = df_train['x'][:slice_size].values
    y_train = df_train['y'][:slice_size].values

    x_test = df_test['x'][:slice_size].values
    y_test = df_test['y'][:slice_size].values

    # Perform gradient descent to get slope (m) and y-intercept (b)
    # Set the step size to something small to avoid over-shooting the minimum
    learning_rate = 0.00005
    steps = 200
    m, b, mse = linear_regression(x_train, y_train, learning_rate, steps)

    # Compute the fit line and show the R^2 error
    y_hat = m * x_test + b
    print('R^2 = {:.4f}'.format(r_squared(y_test, y_hat)))

    print('m={:.4f}, b={:.4f}'.format(m, b))

    # Show a scatter plot of the test data with the calculated line superimposed
    fig, ax = plt.subplots(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.scatter(x_test, y_test)
    plt.plot(x_test, y_hat, color='red')
    plt.title('Linear Regression')

    # Show a line plot of Mean Squared Error decreasing by iteration of gradient descent
    plt.subplot(1, 2, 2)
    x_vals = range(steps)
    plt.ylim(0, 200)
    plt.xlim(0, 50)
    plt.plot(x_vals, mse)
    plt.title('Mean Squared Error')
    plt.xlabel('Iteration Number')
    plt.ylabel('Mean Squared Error')
    plt.show()


if __name__ == '__main__':
    main()
