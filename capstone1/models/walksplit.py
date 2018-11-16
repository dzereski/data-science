"""
walksplit
~~~~~~~~~~~~~~~~
A scikit-learn cross validator for walk forward testing of time
series models
"""

import numpy as np

EXPANDING_WALK = 'expanding'
FIXED_WALK = 'fixed'

MIN_SPLITS = 2


class TimeSeriesWalkSplit:
    """Walk forward cross-validator for time series

    Provides train/test indices to split a time series for
    walk forard validation using either a fixed or expanding
    training set. The size of the test set remains fixed. By
    default, the size of the training set is increased by the
    test size for each fold illustrated below.

    Expanding Walk:

    [fold 0]  ############### Train ###############**** Test ***-------------
    [fold 1]  ############### Train ############################**** Test ***

    If a fixed walk type is chosen then the training set also
    remains fixed for each fold and is moved forward by the
    test size as shown below.

    Fixed Walk:

    [fold 0] ############### Train ###############**** Test ***-------------
    [fold 1] -------------############### Train ###############**** Test ***

    Parameters
    ----------
    test_size: test set size. Stays fixed for each fold.
    train_size: Optional - training set size. Stays fixed for each fold
        in a fixed walk. Grows by test_size for an expanding walk. Will
        default to 3 times the test_size if not specified.
    walk_type: Optional - fixed or expanding. Default is expanding.
    n_splits: Optional - number of splits to generate. Performs the
        last n_splits of total possible given data, train and test sizes.
    start_idx: Optional - index where the walk should begin. Default is 0.

    Returns
    -------
    Train/test indices to split time series samples.

    """

    def __init__(self, test_size, train_size=None, walk_type=EXPANDING_WALK, n_splits=None, start_idx=0):
        self.test_size = test_size
        if train_size is None:
            self.train_size = 3 * test_size
        else:
            self.train_size = train_size

        self.walk_type = walk_type
        self.n_splits = n_splits
        self.start_idx = start_idx

    def _get_max_splits(self, X):
        n_splits = (len(X) - self.train_size) // self.test_size

        return n_splits

    def get_n_splits(self, X=None, y=None, groups=None):
        if self.n_splits is None:
            n_splits = self._get_max_splits(X)
        else:
            n_splits = self.n_splits

        return n_splits

    def split(self, X, y=None, groups=None):
        max_splits = self._get_max_splits(X)

        if max_splits < MIN_SPLITS:
            raise ValueError('Not enough data to split')

        if self.n_splits is not None and self.n_splits > max_splits:
            raise ValueError('n_splits is greater than the possible max_splits of {}'.format(max_splits))

        if self.n_splits is None:
            start_split = 0
        else:
            start_split = max_splits - self.n_splits

        for n in range(start_split, max_splits):
            if self.walk_type == EXPANDING_WALK:
                train_start_idx = self.start_idx
                test_start_idx = train_start_idx + (self.train_size + (n * self.test_size))
            else:
                train_start_idx = self.start_idx + (n * self.test_size)
                test_start_idx = train_start_idx + self.train_size

            test_end_idx = test_start_idx + self.test_size

            yield (np.arange(train_start_idx, test_start_idx), np.arange(test_start_idx, test_end_idx))
