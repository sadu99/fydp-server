import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from handlers.model.time_series import TimeSeries


def mod_euler_angles(pitch, roll, yaw):
    pitch_offset = pitch[0]
    roll_offset = roll[0]
    yaw_offset = yaw[0]

    for i in range(len(pitch)):
        # offset the angles to center at 0 degrees
        pitch[i] = pitch[i] - pitch_offset
        roll[i] = roll[i] - roll_offset
        yaw[i] = yaw[i] - yaw_offset

        # mod the angles to eliminate discontinuities
        # Don't need roll and yaw for now, mod if needed
        while pitch[i] < -90 or pitch[i] > 90:
            if pitch[i] < -90:
                pitch[i] = pitch[i] + 180
            if pitch[i] > 90:
                pitch[i] = pitch[i] - 180


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
x_threshold = 0.6
file_idx = '2'
activity = 'Jump'
path_left = "../supervised_data/%s/%s_acc_left.csv" % (activity, file_idx)
df = pd.read_csv(path_left)

# Clean Incoming Data
acc_x_raw = df[['time', 'x']]

# Build TimeSeries Objects
acc_x_ts = TimeSeries(acc_x_raw['time'], acc_x_raw['x'])

# # Extract Spikes
spikes_x = acc_x_ts.get_negative_spikes(x_threshold)

# Build x Graph
plt.figure(figsize=(14, 7))
plt.plot(df['time'], df['x'])
plt.title('%s, x-threshold = %f' % (path_left, x_threshold))
color_bool = 1
for spike in spikes_x:
    color_bool = color_bool * -1
    data["average_max_peak_acc_x"] += spike["max_value"] / len(spikes_x)
    data["average_min_peak_acc_x"] += spike["min_value"] / len(spikes_x)
    data["average_peak_acc_difference_x"] += (spike["max_value"] - spike["min_value"]) / len(spikes_x)
    plt.plot(spike["time"], spike["max_value"], 'ro')
    plt.plot(spike["time"], spike["min_value"], 'go')
    if color_bool == 1:
        plt.plot(acc_x_ts.time_axis[spike["start_index"]:spike["end_index"]], spike["values"], '--r')
    else:
        plt.plot(acc_x_ts.time_axis[spike["start_index"]:spike["end_index"]], spike["values"], '--g')


path_right = "../supervised_data/%s/%s_acc_right.csv" % (activity, file_idx)
df = pd.read_csv(path_right)

# Clean Incoming Data
acc_x_raw = df[['time', 'x']]

# Build TimeSeries Objects
acc_x_ts = TimeSeries(acc_x_raw['time'], acc_x_raw['x'])

# # Extract Spikes
spikes_x = acc_x_ts.get_negative_spikes(x_threshold)

# Build x Graph
plt.figure(figsize=(14, 7))
plt.plot(df['time'], df['x'])
plt.title('%s, x-threshold = %f' % (path_right, x_threshold))
for spike in spikes_x:
    color_bool = color_bool * -1
    data["average_max_peak_acc_x"] += spike["max_value"] / len(spikes_x)
    data["average_min_peak_acc_x"] += spike["min_value"] / len(spikes_x)
    data["average_peak_acc_difference_x"] += (spike["max_value"] - spike["min_value"]) / len(spikes_x)
    plt.plot(spike["time"], spike["max_value"], 'ro')
    plt.plot(spike["time"], spike["min_value"], 'go')
    if color_bool == 1:
        plt.plot(acc_x_ts.time_axis[spike["start_index"]:spike["end_index"]], spike["values"], '--r')
    else:
        plt.plot(acc_x_ts.time_axis[spike["start_index"]:spike["end_index"]], spike["values"], '--g')


# path_euler_left = "../supervised_data/Testing/%s_euler_left.csv" % file_idx
# df = pd.read_csv(path_euler_left)
#
# pitch_threshold = 0.75
# pitch = np.array(df['pitch'])
# roll = np.array(df['roll'])
# yaw = np.array(df['yaw'])
# mod_euler_angles(pitch, roll, yaw)
#
# pitch_ts = TimeSeries(df['time'], pd.Series(pitch))
# pitch_spikes = pitch_ts.get_negative_spikes(pitch_threshold)
#
# plt.figure(figsize=(14, 7))
# plt.plot(df['time'], pd.Series(pitch))
# plt.title("pitch, threshold = %s" % pitch_threshold)
# for spike in pitch_spikes:
#     plt.plot(pitch_ts.time_axis[spike["start_index"]:spike["end_index"]], spike["values"], '--r')



# Show Graph
plt.show()
