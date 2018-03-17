import peakutils as peakutils
import numpy as np
import pandas as pd

class TimeSeries:
    def __init__(self, time_axis, data_axis):
        self.time_axis = time_axis
        self.data_axis = data_axis
        self.max_time = max(time_axis) / 1000
        self.data_points_per_second = int(len(self.time_axis) / self.max_time)
        self.spike_max_radius = 2 * self.data_points_per_second / 5

    def get_spike(self, index, last_spike_end):
        step_size = 3 * self.data_points_per_second / 10 # number of points used to calculate variance
        variance_threshold = 0.001 # threshold used to determine if the motion is at rest
        left_variance = right_variance = 9999
        data_arr = np.array(self.data_axis)
        left_stable = right_stable = True  # true if left and right side of the spike represent resting state

        current_idx = index
        while current_idx - step_size >= last_spike_end and left_variance > variance_threshold:
            left_variance = np.var(data_arr[current_idx - step_size + 1: current_idx + 1])
            current_idx -= 1
        if current_idx - step_size >= last_spike_end:
            start_index = current_idx - step_size + 1
        else:
            start_index = last_spike_end
            left_stable = False

        current_idx = index
        while current_idx <= len(data_arr) - step_size and \
                current_idx - index + step_size < self.spike_max_radius and \
                right_variance > variance_threshold:
            right_variance = np.var(data_arr[current_idx: current_idx + step_size])
            current_idx += 1
        if current_idx > len(data_arr) - step_size - 1:
            end_index = len(data_arr) - 1
            right_stable = False
        elif current_idx - index + step_size < self.spike_max_radius:
            end_index = index + self.spike_max_radius - 1 if index + self.spike_max_radius < len(data_arr) else len(data_arr) - 1
            right_stable = False
        elif current_idx <= len(data_arr) - step_size:
            end_index = current_idx + step_size - 1

        spike_values = self.data_axis[start_index:end_index]
        return {
            "index": index,
            "values": spike_values,
            "time": self.time_axis[index],
            "min_value": min(spike_values),
            "start_index": start_index,
            "end_index": end_index,
            "max_value": max(spike_values),
            "variance": np.var(spike_values),
            "left_stable": left_stable,
            "right_stable": right_stable
        }

    def get_spikes(self, threshold):
        spike_indices = peakutils.indexes(self.data_axis, thres=threshold, min_dist=2*self.spike_max_radius)
        spikes = []
        last_spike_end = 0

        for index in spike_indices:
            spike = self.get_spike(index, last_spike_end)
            last_spike_end = spike["end_index"]
            spikes.append(spike)
        return spikes

    def get_negative_spikes(self, threshold):
        spikes = []
        negative_ts = pd.Series([val * -1 for val in self.data_axis.values])
        spike_indices = peakutils.indexes(negative_ts, thres=threshold, min_dist=2*self.spike_max_radius)
        last_spike_end = 0

        for index in spike_indices:
            spike = self.get_spike(index, last_spike_end)
            last_spike_end = spike["end_index"]
            spikes.append(spike)
        return spikes

    def get_time_axis(self):
        return self.time_axis

    def get_data_axis(self):
        return self.data_axis