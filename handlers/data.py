import peakutils as peakutils


class TimeSeries:
    def __init__(self, time_axis, data_axis):
        self.time_axis = time_axis
        self.data_axis = data_axis
        self.max_time = max(time_axis)
        self.data_points_per_second = int(len(time_axis) / self.max_time)

    def get_spike_windows(self):
        min_dist_between_spikes = self.data_points_per_second / 2
        spike_indices = peakutils.indexes(self.data_axis, thres=0.75, min_dist=min_dist_between_spikes)

        spike_windows = []
        for spike_index in spike_indices:
            start_index = spike_index - self.data_points_per_second / 5
            end_index = spike_index + self.data_points_per_second / 5
            time_axis = self.time_axis[start_index: end_index]
            data_axis = self.data_axis[start_index: end_index]
            spike_window = SpikeWindow(time_axis, data_axis, spike_index)
            spike_windows.append(spike_window)
        return spike_windows

    def get_time_axis(self):
        return self.time_axis

    def get_data_axis(self):
        return self.data_axis


class SpikeWindow(TimeSeries):
    def __init__(self, time_axis, data_axis, spike_index):
        TimeSeries.__init__(self, time_axis, data_axis)
        self.spike_time = self.time_axis[spike_index]
        self.spike_value = self.data_axis[spike_index]

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
