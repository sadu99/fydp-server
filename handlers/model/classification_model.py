# Split iris data in train and test data
# A random permutation, to split the data randomly
import pandas as pd
import os
import config
import numpy as np
from handlers.model.time_series import TimeSeries
from sklearn.neighbors import KNeighborsClassifier
import matplotlib.pyplot as plt


class ClassificationModel:
    def __init__(self):
        self.model = KNeighborsClassifier()

    def mod_euler_angles(self, pitch, roll, yaw):
        pitch_offset = pitch[0]
        roll_offset = roll[0]
        yaw_offset = yaw[0]

        for i in range(len(pitch)):
            # offset the angles to center at 0 degrees
            pitch[i] = pitch[i] - pitch_offset
            roll[i] = roll[i] - roll_offset
            yaw[i] = yaw[i] - yaw_offset

            # mod the angles to eliminate discontinuities
            # Don't need yaw for now, mod if needed
            while pitch[i] < -90 or pitch[i] > 90:
                if pitch[i] < -90:
                    pitch[i] = pitch[i] + 180
                if pitch[i] > 90:
                    pitch[i] = pitch[i] - 180

            while roll[i] < -90 or roll[i] > 90:
                if roll[i] < -90:
                    roll[i] = roll[i] + 180
                if roll[i] > 90:
                    roll[i] = roll[i] - 180

    def get_severity(self, angle):
        if angle <= 6.0:
            return 0.25
        if angle <= 10.0:
            return 0.50
        if angle <= 15.0:
            return 0.75
        return 1.0

    def train_model(self):
        classes = ["Jump", "Walk", "Run", "Noise"]
        config.training_threshold_map = {
            1: {"Jump": 0.50,  "Walk": 0.45, "Run": 0.7, "Noise": 0.4},
            2: {"Jump": 0.55, "Walk": 0.5, "Run": 0.65, "Noise": 0.4},
            3: {"Jump": 0.50, "Walk": 0.5, "Run": 0.7, "Noise": 0.4}
            # 4: {"Jump": 0.55, "Walk": 0.8, "Run": 0.7, "Load": 0.51, "Noise": 0.5}
        }
        data = []
        targets = [] # what class each point actually is

        for i in range(len(classes)):
            files_ended = False
            file_idx = 0
            left_or_right = "left"
            while not files_ended:
                # Read CSV File
                DATA_PATH = os.path.join(config.ROOT_DIR, 'supervised_data')
                file_idx += 1
                path = "%s/%s/%s_acc_%s.csv" % (DATA_PATH, classes[i], file_idx, left_or_right)
                if not os.path.exists(path):
                    files_ended = True
                    continue
                df = pd.read_csv(path)
                left_or_right = "right" if left_or_right == "left" else "left"

                # Build TimeSeries Objects
                acc_x_ts = TimeSeries(df['time'], df['x'])
                acc_y_ts = TimeSeries(df['time'], df['y'])
                acc_z_ts = TimeSeries(df['time'], df['z'])

                # Get peaks based on x-axis
                spikes_x = acc_x_ts.get_negative_spikes(config.training_threshold_map[file_idx][classes[i]])
                for spike in spikes_x:
                    max_y_value = max(acc_y_ts.data_axis[spike["start_index"]: spike["end_index"]])
                    min_y_value = min(acc_y_ts.data_axis[spike["start_index"]: spike["end_index"]])

                    max_z_value = max(acc_z_ts.data_axis[spike["start_index"]: spike["end_index"]])
                    min_z_value = min(acc_z_ts.data_axis[spike["start_index"]: spike["end_index"]])

                    data.append([
                        spike["max_value"],
                        spike["min_value"],
                        # spike["max_value"] - spike["min_value"],
                        # max_y_value,
                        # min_y_value,
                        # max_y_value - min_y_value,
                        max_z_value,
                        min_z_value,
                        # max_z_value - min_z_value,
                        spike["variance"]
                    ])
                    targets.append(i)

        # Create and fit a nearest-neighbor classifier
        self.model.fit(np.asarray(data), np.asarray(targets))

    def test_classifier(self, file_path):
        data_test = []

        # Read CSV File
        acc_file = pd.read_csv("../../data/Testing/3_acc_left.csv")

        # Build TimeSeries Objects
        acc_x_ts = TimeSeries(acc_file['time'], acc_file['x'])
        acc_y_ts = TimeSeries(acc_file['time'], acc_file['y'])
        acc_z_ts = TimeSeries(acc_file['time'], acc_file['z'])

        # Extract Spikes
        spikes_x = acc_x_ts.get_negative_spikes(config.TEST_THRESHOLD)
        for spike in spikes_x:
            max_y_value = max(acc_y_ts.data_axis[spike["start_index"]: spike["end_index"]])
            min_y_value = min(acc_y_ts.data_axis[spike["start_index"]: spike["end_index"]])

            max_z_value = max(acc_z_ts.data_axis[spike["start_index"]: spike["end_index"]])
            min_z_value = min(acc_z_ts.data_axis[spike["start_index"]: spike["end_index"]])

            data_test.append([
                spike["max_value"],
                spike["min_value"],
                # spike["max_value"] - spike["min_value"],
                # max_y_value,
                # min_y_value,
                # max_y_value - min_y_value,
                max_z_value,
                min_z_value,
                # max_z_value - min_z_value,
                spike["variance"]
            ])

        predicted = self.model.predict(data_test)
        print predicted
        return predicted

    def get_abduction_angles(self, file_name):
        home = os.path.expanduser("~")
        data_test = []
        jumps = []
        sides = ["left", "right"]

        for side in sides:
            # Get abduction angles for left leg
            # Read CSV File
            acc_file = pd.read_csv("%s/data/%s_acc_%s.csv" % (home, file_name, side))
            euler_file = pd.read_csv("%s/data/%s_euler_%s.csv" % (home, file_name, side))

            # Build TimeSeries Objects
            acc_x_ts = TimeSeries(acc_file['time'], acc_file['x'])
            acc_y_ts = TimeSeries(acc_file['time'], acc_file['y'])
            acc_z_ts = TimeSeries(acc_file['time'], acc_file['z'])

            # Get euler angles
            pitch = np.array(euler_file['pitch'])
            roll = np.array(euler_file['roll'])
            yaw = np.array(euler_file['yaw'])
            euler_times = np.array(euler_file['time'])
            self.mod_euler_angles(pitch, roll, yaw)
            pitch_ts = TimeSeries(euler_file['time'], euler_file['pitch'])
            roll_ts = TimeSeries(euler_file['time'], euler_file['roll'])

            # Extract Spikes
            spikes_x = acc_x_ts.get_negative_spikes(config.TEST_THRESHOLD)
            for spike in spikes_x:
                max_y_value = max(acc_y_ts.data_axis[spike["start_index"]: spike["end_index"]])
                min_y_value = min(acc_y_ts.data_axis[spike["start_index"]: spike["end_index"]])

                max_z_value = max(acc_z_ts.data_axis[spike["start_index"]: spike["end_index"]])
                min_z_value = min(acc_z_ts.data_axis[spike["start_index"]: spike["end_index"]])

                data_test.append([
                    spike["max_value"],
                    spike["min_value"],
                    # spike["max_value"] - spike["min_value"],
                    # max_y_value,
                    # min_y_value,
                    # max_y_value - min_y_value,
                    max_z_value,
                    min_z_value,
                    # max_z_value - min_z_value,
                    spike["variance"]
                ])

            predictions = self.model.predict(data_test)
            acc_times = np.array(acc_file['time'])
            prev_start_idx = prev_end_idx = 0

            # plt.figure(figsize=(14, 7))
            # plt.plot(euler_file['time'], euler_file['roll'])
            # plt.title('roll')

            for idx, prediction in enumerate(predictions):
                # process a jump
                if prediction == 0:
                    start_time = acc_times[spikes_x[idx]["start_index"]]
                    end_time = acc_times[spikes_x[idx]["end_index"]]

                    while euler_times[prev_start_idx] < start_time:
                        prev_start_idx += 1
                    euler_start_idx = prev_start_idx
                    euler_start_angle = roll[euler_start_idx]
                    while euler_times[prev_start_idx] < end_time:
                        prev_start_idx += 1
                    euler_end_idx = prev_start_idx
                    euler_end_angle = roll[euler_end_idx]

                    peak_angle = min(roll[euler_start_idx:euler_end_idx])
                    abduction_angle = abs(peak_angle - euler_end_angle) if not spikes_x[idx]["left_stable"] and spikes_x[idx]["right_stable"] \
                        else abs(peak_angle - euler_start_angle)

                    jump = {
                        "abduction_angle": abduction_angle,
                        "jump_time": spikes_x[idx]["time"],
                        "severity": self.get_severity(abduction_angle),
                        "leg": side
                    }
                    jumps.append(jump)
                    print abduction_angle
                    # plt.plot(roll_ts.time_axis[euler_start_idx:euler_end_idx], roll_ts.data_axis[euler_start_idx:euler_end_idx], '--r')
            # plt.show()
        return jumps
