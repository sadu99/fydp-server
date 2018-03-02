# Split iris data in train and test data
# A random permutation, to split the data randomly
import json
import pandas as pd

import numpy as np
from sklearn import datasets
#
# iris = datasets.load_iris()
# iris_X = iris.data
# iris_y = iris.target
#
#
# print iris
# print ''
# print iris.data
# print ''
# print iris.target
# print ''
#
# np.random.seed(0)
# indices = np.random.permutation(len(iris_X))
# iris_X_train = iris_X[indices[:-10]]
# iris_y_train = iris_y[indices[:-10]]
# iris_X_test  = iris_X[indices[-10:]]
# iris_y_test  = iris_y[indices[-10:]]
#
# # Create and fit a nearest-neighbor classifier
# from sklearn.neighbors import KNeighborsClassifier
# knn = KNeighborsClassifier()
# knn.fit(iris_X_train, iris_y_train)
# # KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski',
# #            metric_params=None, n_jobs=1, n_neighbors=5, p=2,
# #            weights='uniform')
#
# print knn.predict(iris_X_test)


from handlers.model.time_series import TimeSeries

classes = ["jump", "walk", "run"]
threshold_map = {"jump": 0.85, "walk": 0.85, "run": 0.75, "pivot": 0.8}
data = []
targets = []

for i in range(len(classes)):

    # Read CSV File
    df = pd.read_csv("%s.csv" % classes[i])

    # Build TimeSeries Objects
    acc_x_ts = TimeSeries(df['elapsed (s)'], df['x-axis (g)'])
    acc_y_ts = TimeSeries(df['elapsed (s)'], df['y-axis (g)'])
    acc_z_ts = TimeSeries(df['elapsed (s)'], df['z-axis (g)'])

    # Extract Spikes
    spikes_x = acc_x_ts.get_spikes(threshold_map[classes[i]])

    for spike in spikes_x:

        start_index = spike["index"] - acc_x_ts.data_points_per_second / 5
        end_index = spike["index"] + acc_x_ts.data_points_per_second / 5

        if start_index < 0:
            start_index = 0

        if end_index >= len(acc_x_ts.time_axis):
            end_index = len(acc_x_ts.time_axis) - 1

        max_y_value = max(acc_y_ts.data_axis[start_index: end_index])
        min_y_value = min(acc_y_ts.data_axis[start_index: end_index])

        max_z_value = max(acc_z_ts.data_axis[start_index: end_index])
        min_z_value = min(acc_z_ts.data_axis[start_index: end_index])

        data.append([
            spike["max_value"],
            spike["min_value"],
            spike["max_value"] - spike["min_value"],
            max_y_value,
            min_y_value,
            max_y_value - min_y_value,
            max_z_value,
            min_z_value,
            max_z_value - min_z_value
        ])
        targets.append(i)

indices = np.random.permutation(len(data))

data_train = np.asarray([data[i] for i in indices[:int(0.6 * len(indices))]])
data_test = np.asarray([data[i] for i in indices[int(0.6 * len(indices)):]])
targets_train = np.asarray([targets[i] for i in indices[:int(0.6 * len(indices))]])
targets_test = np.asarray([targets[i] for i in indices[int(0.6 * len(indices)):]])

# Create and fit a nearest-neighbor classifier
from sklearn.neighbors import KNeighborsClassifier

knn = KNeighborsClassifier()

knn.fit(data_train, targets_train)
# KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski',
#            metric_params=None, n_jobs=1, n_neighbors=5, p=2,
#            weights='uniform')



# data_test = []
#
# # Read CSV File
# df = pd.read_csv("test_down_acc.csv")
#
# # Build TimeSeries Objects
# acc_x_ts = TimeSeries(df['elapsed (s)'], df['x-axis (g)'])
# acc_y_ts = TimeSeries(df['elapsed (s)'], df['y-axis (g)'])
# acc_z_ts = TimeSeries(df['elapsed (s)'], df['z-axis (g)'])
#
# # Extract Spikes
# spikes_x = acc_x_ts.get_spikes(0.76)
#
# for spike in spikes_x:
#
#     start_index = spike["index"] - acc_x_ts.data_points_per_second / 5
#     end_index = spike["index"] + acc_x_ts.data_points_per_second / 5
#
#     if start_index < 0:
#         start_index = 0
#
#     if end_index >= len(acc_x_ts.time_axis):
#         end_index = len(acc_x_ts.time_axis) - 1
#
#     max_y_value = max(acc_y_ts.data_axis[start_index: end_index])
#     min_y_value = min(acc_y_ts.data_axis[start_index: end_index])
#
#     max_z_value = max(acc_z_ts.data_axis[start_index: end_index])
#     min_z_value = min(acc_z_ts.data_axis[start_index: end_index])
#
#     data_test.append([
#         spike["max_value"],
#         spike["min_value"],
#         spike["max_value"] - spike["min_value"],
#         max_y_value,
#         min_y_value,
#         max_y_value - min_y_value,
#         max_z_value,
#         min_z_value,
#         max_z_value - min_z_value
#     ])


predicted = knn.predict(data_test)
print predicted
print ''

correct, wrong = 0, 0

for i in range(len(predicted)):

    if predicted[i] == targets_test[i]:
        correct += 1
    else:
        wrong += 1

print ''
print 'total:', len(targets_test), '\ncorrect:', correct, '\nwrong:', wrong
