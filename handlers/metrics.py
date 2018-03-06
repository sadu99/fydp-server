import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from handlers.model.time_series import TimeSeries

# Create a colormap
colormap = np.array(['red', 'black'])

# data = {
#     "acc_x": {
#         "peak_acc": 0,
#         "max_difference": 0,
#         "average": 0,
#     }, "acc_y": {
#         "peak_acc": 0,
#         "max_difference": 0,
#         "average": 0,
#     }, "acc_z": {
#         "peak_acc": 0,
#         "max_difference": 0,
#         "average": 0,
#     }
# }

data = {
    "average_max_peak_acc_x": 0,
    "average_max_peak_acc_y": 0,
    "average_max_peak_acc_z": 0,
    "average_min_peak_acc_x": 0,
    "average_min_peak_acc_y": 0,
    "average_min_peak_acc_z": 0,
    "average_peak_acc_difference_x": 0,
    "average_peak_acc_difference_y": 0,
    "average_peak_acc_difference_z": 0
}

# Read CSV File
file = "Testing/3_right_acc.csv"
x_threshold = 0.5
# y_threshold = 0.8
# z_threshold = 0.8
df = pd.read_csv("../Supervised Data/%s" % file)

# Clean Incoming Data
acc_x_raw = df[['elapsed (s)', 'x-axis (g)']]
acc_y_raw = df[['elapsed (s)', 'y-axis (g)']]
acc_z_raw = df[['elapsed (s)', 'z-axis (g)']]

# Build TimeSeries Objects
acc_x_ts = TimeSeries(acc_x_raw['elapsed (s)'], acc_x_raw['x-axis (g)'])
acc_y_ts = TimeSeries(acc_y_raw['elapsed (s)'], acc_y_raw['y-axis (g)'])
acc_z_ts = TimeSeries(acc_z_raw['elapsed (s)'], acc_z_raw['z-axis (g)'])

# Extract Spike Windows
spike_windows_x = acc_x_ts.get_spike_windows()
spike_windows_y = acc_y_ts.get_spike_windows()
spike_windows_z = acc_z_ts.get_spike_windows()

# Extract Spikes
spikes_x = acc_x_ts.get_spikes(x_threshold)
# spikes_y = acc_y_ts.get_spikes(y_threshold)
# spikes_z = acc_z_ts.get_spikes(z_threshold)

# Build x Graph
plt.figure(figsize=(14, 7))
plt.plot(df['elapsed (s)'], df['x-axis (g)'])
plt.title('%s, x-threshold = %f' % (file, x_threshold))
for spike in spikes_x:
    data["average_max_peak_acc_x"] += spike["max_value"] / len(spikes_x)
    data["average_min_peak_acc_x"] += spike["min_value"] / len(spikes_x)
    data["average_peak_acc_difference_x"] += (spike["max_value"] - spike["min_value"]) / len(spikes_x)
    plt.plot(spike["time"], spike["max_value"], 'ro')
    plt.plot(spike["time"], spike["min_value"], 'go')

for sw in spike_windows_x:
    # data["acc_x"]["peak_acc"] += sw.get_spike_value() / len(spike_windows_x)
    # data["acc_x"]["max_difference"] += sw.get_max_difference() / len(spike_windows_x)
    # data["acc_x"]["average"] += sw.get_average_value() / len(spike_windows_x)
    plt.plot(sw.time_axis, sw.data_axis, '--r')

# Build y Graph
# plt.figure(figsize=(14, 7))
# plt.plot(df['elapsed (s)'], df['y-axis (g)'])
# plt.title('%s, y-threshold = %f' % (file, y_threshold))
# for spike in spikes_y:
#     data["average_max_peak_acc_y"] += spike["max_value"] / len(spikes_y)
#     data["average_min_peak_acc_y"] += spike["min_value"] / len(spikes_y)
#     data["average_peak_acc_difference_y"] += (spike["max_value"] - spike["min_value"]) / len(spikes_y)
#     plt.plot(spike["time"], spike["max_value"], 'ro')
#     plt.plot(spike["time"], spike["min_value"], 'go')

# for sw in spike_windows_y:
#     data["acc_y"]["peak_acc"] += sw.get_spike_value() / len(spike_windows_y)
#     data["acc_y"]["max_difference"] += sw.get_max_difference() / len(spike_windows_y)
#     data["acc_y"]["average"] += sw.get_average_value() / len(spike_windows_y)
#     plt.plot(sw.time_axis, sw.data_axis, '--r')

# Build z Graph
# plt.figure(figsize=(14, 7))
# plt.plot(df['elapsed (s)'], df['z-axis (g)'])
# plt.title('%s, z-threshold = %f' % (file, z_threshold))
# for spike in spikes_z:
#     data["average_max_peak_acc_z"] += spike["max_value"] / len(spikes_z)
#     data["average_min_peak_acc_z"] += spike["min_value"] / len(spikes_z)
#     data["average_peak_acc_difference_z"] += (spike["max_value"] - spike["min_value"]) / len(spikes_z)
#     plt.plot(spike["time"], spike["max_value"], 'ro')
#     plt.plot(spike["time"], spike["min_value"], 'go')

# for sw in spike_windows_z:
#     data["acc_z"]["peak_acc"] += sw.get_spike_value() / len(spike_windows_z)
#     data["acc_z"]["max_difference"] += sw.get_max_difference() / len(spike_windows_z)
#     data["acc_z"]["average"] += sw.get_average_value() / len(spike_windows_z)
#     plt.plot(sw.time_axis, sw.data_axis, '--r')

# plt.figure()
# for sw in spike_windows_x:
#     # print sw.get_spike_value()
#     # sw.data_axis = [i - offset for i in sw.data_axis]
#     # print sw.get_max_difference()
#     plt.plot(sw.get_spike_value(), sw.get_average_value(), 'ro')
#
# model = KMeans(n_clusters=2)
# x = [[sw.get_spike_value() for sw in spike_windows_x], [sw.get_average_value() for sw in spike_windows_x]]
# model.fit(x)
#
# plt.figure()
# plt.scatter([sw.get_spike_value() for sw in spike_windows_x], [sw.get_average_value() for sw in spike_windows_x],
#             c=colormap[model.labels_])

print data

# Show Graph
plt.show()
