"""
walksplit_example
~~~~~~~~~~~~~~~~
Simple examples for TimeSeriesWalkSplit
"""
import numpy as np

from walksplit import TimeSeriesWalkSplit


def main():

    TEST_SIZE = 7
    TRAIN_SIZE = TEST_SIZE * 8
    DATA_SIZE = TRAIN_SIZE + (TEST_SIZE * 5)

    X = np.zeros(DATA_SIZE)

    tscv = TimeSeriesWalkSplit(TEST_SIZE, TRAIN_SIZE, n_splits=3)

    for (train_index, test_index) in tscv.split(X):
        print(train_index)
        print(test_index)
        print('-' * 20)

    print('N Splits = {}'.format(tscv.get_n_splits(X)))


if __name__ == '__main__':
    main()
