import peakutils as peakutils
import pandas as pd
import scipy.integrate as integrate
import scipy.special as special


class TimeSeries:
    def __init__(self, time_axis, data_axis):
        self.time_axis = time_axis
        self.data_axis = data_axis
        self.max_time = max(time_axis)

        self.data_points_per_second = int(len(self.time_axis) / self.max_time)

    def get_spikes(self, threshold):
        min_dist_between_spikes = self.data_points_per_second / 2
        spike_indices = peakutils.indexes(self.data_axis, thres=threshold, min_dist=min_dist_between_spikes)

        spikes = []
        for index in spike_indices:

            start_index = index - self.data_points_per_second / 5
            end_index = index + self.data_points_per_second / 5

            if start_index < 0:
                start_index = 0

            if end_index >= len(self.time_axis):
                end_index = len(self.time_axis) - 1

            spikes.append({
                "index": index,
                "time": self.time_axis[index],
                "min_value": min(self.data_axis[start_index: end_index]),
                "max_value": self.data_axis[index]
            })

        return spikes



    def get_spike_windows(self):
        min_dist_between_spikes = self.data_points_per_second / 2
        spike_indices = peakutils.indexes(self.data_axis, thres=0.75, min_dist=min_dist_between_spikes)

        spike_windows = []
        for spike_index in spike_indices:
            start_index = spike_index - self.data_points_per_second / 5
            end_index = spike_index + self.data_points_per_second / 5

            if start_index < 0:
                start_index = 0

            if end_index >= len(self.time_axis):
                end_index = len(self.time_axis) - 1

            time_axis = self.time_axis[start_index: end_index]
            data_axis = self.data_axis[start_index: end_index]
            spike_window = SpikeWindow(time_axis, data_axis, spike_index)
            spike_windows.append(spike_window)
        return spike_windows

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
