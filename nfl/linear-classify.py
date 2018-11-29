"""
linear-classify
~~~~~~~~~~~~~~~~
Simple example to use linear classifiers like Logistic Regression and
Linear SVM to classify NFL offensive linemen and wide receivers
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC


def get_players(fname):
    """Read WR and OL players from a CSV file and return as
    a DataFrame.
    """

    df = pd.read_csv(fname)

    # Filter the offensive line players and just label them all as "OL"
    ol = df[(df.position == 'C') | (df.position == 'G') | (df.position == 'T') | (df.position == 'OT')].copy()
    ol.position = 'OL'

    # Filter the wide receivers
    wr = df[(df.position == 'WR')]

    # Create a single DF with all players and carve out X and y
    return ol.append(wr)


def plot_boundary(clf, ax):
    """ Plot the "decision" boundary. It's not really a decision boundary for Logistic
    Regression but helpful to visualize anyway.  It is the decision boundary for Linear SVC.
    """

    xlim = ax.get_xlim()
    size = int(xlim[1] - int(xlim[0]))
    x = np.linspace(xlim[0], xlim[1], size)

    W = clf.coef_[0]
    B = clf.intercept_[0]

    # W0*X + W1*Y + B = 0.  Solving for Y gives
    # -W1*Y = W0*X + B
    # Y = (W0*X + B) / -W1
    # Y = -W0/W1 * X + B / -W1
    # a = -W0/W1
    # b = -B/W1
    # y = ax + b
    a = -(W[0] / W[1])
    b = -(B / W[1])

    y = a * x + b

    ax.plot(x, y, color='Black')


def main():
    # Read the roster of 2015 players.  This will be used to classify
    players = get_players('nfl-players-2015.csv')

    # Split out X and y then create training & test sets
    X = players[['height', 'weight']]
    y = players['position']

    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

    # Train the classifier
    model = LogisticRegression()
    # model = LinearSVC()
    clf = model.fit(X_train, y_train)

    # Check the test score
    print('Test Score = {:.2f}%'.format(clf.score(X_test, y_test) * 100.0))

    # Create a scatter plot of 2015 players and the "decision" boundary line
    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_xlim(60, 85)
    ax.set_ylim(150, 400)
    players[(players.position == 'OL')].plot.scatter(x='height', y='weight', color='Blue', label='OL', ax=ax)
    ax.annotate('Offensive Line', xy=(62, 290), xytext=(62, 290))

    players[(players.position == 'WR')].plot.scatter(x='height', y='weight', color='Pink', label='WR', ax=ax)
    ax.annotate('Wide Receiver', xy=(82, 190), xytext=(82, 190))

    plt.xlabel('Height')
    plt.ylabel('Weight')
    plt.title('NFL O-Linemen & Wide Receivers')

    # Use the model to classify current Packers players
    players = get_players('nfl-players-2018.csv')
    packers = players[(players.team == 'Packers')]
    packers = packers.drop(['team', 'age', 'years', 'school'], axis=1)

    X_new = packers[['height', 'weight']]

    pred = clf.predict(X_new)
    packers['pred_position'] = pred

    ol = packers[(packers.position == 'OL')]
    ol.plot.scatter(x='height', y='weight', color='Green', marker='X', label='Packers OL', s=ol.weight / 2, ax=ax)
    wr = packers[(packers.position == 'WR')]
    wr.plot.scatter(x='height', y='weight', color='Gold', label='Packers WR', marker='*', s=wr.weight, ax=ax)

    plot_boundary(clf, ax)

    print(packers)

    plt.show()


if __name__ == '__main__':
    main()
