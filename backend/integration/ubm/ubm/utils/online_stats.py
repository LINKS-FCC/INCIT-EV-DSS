import numpy as np
from scipy import stats


class OnlineStats:
    """
    Allows to calculate online statistics on the matrix of interests.

    Based on:
    Welford's online algorithm
    https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Welford.27s_online_algorithm
    """

    def __init__(self):
        self.m = 0.0
        self.m2 = None
        self.count = 0
        self.count_new = np.zeros(shape=(24, 24))
        self.m_new = 0.0

    
    def update_new(self, new_value):
        """
        new function to perform average in starting_soc and final_soc without considering cells with 0 value inside
        """
        if self.count == 0:
            self.m_new = new_value.copy()
            self.m = new_value.copy()
            for i in range(24):
                for j in range(24):
                    if self.m[i][j] != 0:
                        self.count_new[i][j] = 1
            self.count += 1
            return
        self.count += 1
        for i in range(24):
            for j in range(24):
                if new_value[i][j] == 0:
                    continue
                self.m_new[i][j] += new_value[i][j] 
                self.count_new[i][j] += 1
                self.m[i][j] = self.m_new[i][j]/self.count_new[i][j]


    def update(self, new_value):
        """
        For a new value, compute the new count, new mean, the new M2.
        `m` accumulates the mean of the entire dataset.
        `m2` aggregates the squared distance from the mean.
        `count` aggregates the number of samples seen so far.

        Parameters
        ----------
        new_value: np.ndarray
            New value to take into account in the calculation.
        """
        self.count += 1
        delta = new_value - self.m
        self.m += delta / self.count
        delta2 = new_value - self.m
        if self.m2 is None:
            self.m2 = delta * delta2
        else:
            self.m2 += delta * delta2

    @property
    def mean(self):
        """
        Get the current mean.

        Returns
        -------
        mean: np.ndarray
            Mean Matrix
        """
        if self.count < 2:
            return float("nan")
        else:
            return self.m

    @property
    def var(self):
        """
        Get the current variance.

        Returns
        -------
        var: np.ndarray
            Variance Matrix
        """
        if self.count < 2:
            return float("nan")
        else:
            return self.m2 / self.count

    @property
    def sample_var(self):
        """
        Get the current sample variance.

        Returns
        -------
        sample_variance: np.ndarray
            Sample Matrix
        """
        if self.count < 2:
            return float("nan")
        else:
            return self.m2 / (self.count - 1)

    def get_mean_confidence_interval(self, confidence=0.95):
        """
        Get the Confidence Interval radius given the confidence ratio.

        Parameters
        ----------
        confidence: float
            Level of confidence

        Returns
        -------
        confidence_matrix: np.ndarray
            Matrix with absolute confidence interval

        """
        if self.count < 30:
            return None
        # https://stackoverflow.com/questions/15033511/compute-a-confidence-interval-from-sample-data
        m, se = self.m, np.sqrt(self.var) / np.sqrt(self.count)
        h = se * stats.t.ppf((1 + confidence) / 2., self.count - 1)
        return h

    def get_mean_confidence_interval_relative(self, confidence=0.95):
        """
        Get the Confidence Interval radius (relative) given the confidence ratio.

        Parameters
        ----------
        confidence: float
            Level of confidence

        Returns
        -------
        confidence_matrix: np.ndarray
            Matrix with relative confidence interval

        """
        if self.count < 30:
            return None
        h = self.get_mean_confidence_interval(confidence)
        mask = self.m != 0
        return h[mask] / self.m[mask]

    def get_stats(self):
        """
        Retrieve the mean, variance and sample variance from an aggregate

        Returns
        -------
        mean: np.ndarray
            Mean
        variance: np.array
            Variance
        sample_variance: np.array
            Sample Variance
        """
        if self.count < 2:
            return float("nan")
        else:
            (mean, variance, sample_variance) = (self.mean, self.var, self.sample_var)
            return mean, variance, sample_variance


if __name__ == '__main__':
    # Test code
    list_array = []
    stats = OnlineStats()
    for _ in range(100):
        value = np.random.rand(3, 2)
        list_array.append(value)
        stats.update(value)
