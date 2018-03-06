import peakutils as peakutils
import config
import numpy as np
import pandas as pd
import scipy.integrate as integrate
import scipy.special as special

class TimeSeries:
    def __init__(self, time_axis, data_axis):
        self.time_axis = time_axis
        self.data_axis = data_axis
        self.max_time = max(time_axis)
        self.data_points_per_second = int(len(self.time_axis) / self.max_time)
        self.spike_radius = self.data_points_per_second / 4

    def get_spike(self, index):
        start_index = 0 if index < self.spike_radius else index - self.spike_radius
        end_index = len(self.time_axis) - 1 if index > len(self.time_axis) - self.spike_radius else index + self.spike_radius
        return {
            "index": index,
            "time": self.time_axis[index],
            "min_value": min(self.data_axis[start_index: end_index]),
            "start_index": start_index,
            "end_index": end_index,
            "max_value": max(self.data_axis[start_index: end_index]),
            "variance": np.var(self.get_spike_window(index).data_axis)
        }

    def get_spikes(self, threshold):
        spike_indices = peakutils.indexes(self.data_axis, thres=threshold, min_dist=2*self.spike_radius)
        spikes = []

        for index in spike_indices:
            spikes.append(self.get_spike(index))
        return spikes

    def get_negative_spikes(self, threshold):
        spikes = []
        negative_ts = pd.Series([val * -1 for val in self.data_axis.values])
        spike_indices = peakutils.indexes(negative_ts, thres=threshold, min_dist=2*self.spike_radius)

        for index in spike_indices:
            spikes.append(self.get_spike(index))
        return spikes

    def get_spike_windows(self):
        min_dist_between_spikes = self.data_points_per_second / 2
        spike_indices = peakutils.indexes(self.data_axis, thres=config.TEST_THRESHOLD, min_dist=min_dist_between_spikes)

        spike_windows = []
        for spike_index in spike_indices:
            spike_windows.append(self.get_spike_window(spike_index))
        return spike_windows

    def get_spike_window(self, spike_index):
        start_index = spike_index - self.spike_radius
        end_index = spike_index + self.spike_radius

        if start_index < 0:
            start_index = 0

        if end_index >= len(self.time_axis):
            end_index = len(self.time_axis) - 1

        time_axis = self.time_axis[start_index: end_index]
        data_axis = self.data_axis[start_index: end_index]
        return SpikeWindow(time_axis, data_axis, spike_index)

    def get_time_axis(self):
        return self.time_axis

    def get_data_axis(self):
        return self.data_axis

        # def get_clean_series(self):
        #     clean_time = []
        #     clean_data = []
        #     data_length = len(self.time_axis)
        #     i = 1
        #     while i < data_length:
        #         clean_data.append((self.data_axis[i - 1] + self.data_axis[i] + self.data_axis[i + 1]) / 3)
        #         clean_time.append(self.time_axis[i])
        #         i += 3
        #     return clean_time, clean_data


class SpikeWindow(TimeSeries):
    def __init__(self, time_axis, data_axis, spike_index):
        TimeSeries.__init__(self, time_axis, data_axis)
        self.spike_time = self.time_axis[spike_index]
        self.spike_value = self.data_axis[spike_index]
        # self.velocity = self.get_velocity()

    # def get_velocity(self):
    #
    #     result = integrate.quad(lambda x: special.jv(2.5, x), self.get_start_time(), self.get_end_time())

    def get_spike_time(self):
        return self.spike_time

    def get_spike_value(self):
        return self.spike_value

    def get_average_value(self):
        return sum(self.data_axis) / len(self.time_axis)

    def get_start_time(self):
        return self.time_axis[0]

    def get_end_time(self):
        return self.time_axis[-1]

    def get_max_difference(self):
        return max(self.data_axis) - min(self.data_axis)

    def get_clean_series(self):
        return self.time_axis, self.data_axis
