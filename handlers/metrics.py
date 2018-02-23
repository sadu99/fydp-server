import matplotlib.pyplot as plt
import pandas as pd

from data import TimeSeries

# Read CSV File
df = pd.read_csv("test_down_acc.csv")

# Build TimeSeries Objects
acc_x_ts = TimeSeries(df['elapsed (s)'], df['x-axis (g)'])
acc_y_ts = TimeSeries(df['elapsed (s)'], df['y-axis (g)'])
acc_z_ts = TimeSeries(df['elapsed (s)'], df['z-axis (g)'])

# Extract Spike Windows
spike_windows_x = acc_x_ts.get_spike_windows()
spike_windows_y = acc_y_ts.get_spike_windows()
spike_windows_z = acc_z_ts.get_spike_windows()

# Build x Graph
plt.figure(figsize=(14, 7))
plt.plot(df['elapsed (s)'], df['x-axis (g)'])
plt.title('x')
for sw in spike_windows_x:
    plt.plot(sw.time_axis, sw.data_axis, '--r')

# Build y Graph
plt.figure(figsize=(14, 7))
plt.plot(df['elapsed (s)'], df['y-axis (g)'])
plt.title('y')
for sw in spike_windows_y:
    plt.plot(sw.time_axis, sw.data_axis, '--r')

# Build z Graph
plt.figure(figsize=(14, 7))
plt.plot(df['elapsed (s)'], df['z-axis (g)'])
plt.title('z')
for sw in spike_windows_z:
    plt.plot(sw.time_axis, sw.data_axis, '--r')

# Show Graph
plt.show()
