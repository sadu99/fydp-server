import pandas as pd
import os
import config
import numpy as np
from handlers.model.time_series import TimeSeries
from sklearn.neighbors import KNeighborsClassifier
import matplotlib.pyplot as plt


class ClassificationModel:
    def __init__(self):
        self.model = KNeighborsClassifier(weights='distance')

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
        DATA_PATH = os.path.join(config.ROOT_DIR, 'supervised_data')
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
                file_idx += 1
                acc_path = "%s/%s/%s_acc_%s.csv" % (DATA_PATH, classes[i], file_idx, left_or_right)
                euler_path = "%s/%s/%s_euler_%s.csv" % (DATA_PATH, classes[i], file_idx, left_or_right)
                if not os.path.exists(acc_path) or not os.path.exists(euler_path):
                    files_ended = True
                    continue
                acc_file = pd.read_csv("%s/%s/%s_acc_%s.csv" % (DATA_PATH, classes[i], file_idx, left_or_right))
                euler_file = pd.read_csv("%s/%s/%s_euler_%s.csv" % (DATA_PATH, classes[i], file_idx, left_or_right))
                left_or_right = "right" if left_or_right == "left" else "left"

                # Build TimeSeries Objects
                acc_x_ts = TimeSeries(acc_file['time'], acc_file['x'])
                acc_y_ts = TimeSeries(acc_file['time'], acc_file['y'])
                acc_z_ts = TimeSeries(acc_file['time'], acc_file['z'])
                pitch = np.array(euler_file['pitch'])
                roll = np.array(euler_file['roll'])
                yaw = np.array(euler_file['yaw'])
                acc_times = np.array(acc_file['time'])
                euler_times = np.array(euler_file['time'])
                self.mod_euler_angles(pitch, roll, yaw)

                # Get peaks based on x-axis
                spikes_x = acc_x_ts.get_negative_spikes(config.training_threshold_map[file_idx][classes[i]])
                for spike in spikes_x:
                    max_y_value = max(acc_y_ts.data_axis[spike["start_index"]: spike["end_index"]])
                    min_y_value = min(acc_y_ts.data_axis[spike["start_index"]: spike["end_index"]])

                    max_z_value = max(acc_z_ts.data_axis[spike["start_index"]: spike["end_index"]])
                    min_z_value = min(acc_z_ts.data_axis[spike["start_index"]: spike["end_index"]])

                    euler_start_idx, euler_end_idx = self.find_euler_time(spike, acc_times, euler_times)
                    spike_pitch = pitch[euler_start_idx:euler_end_idx]
                    spike_roll = roll[euler_start_idx:euler_end_idx]
                    spike_yaw = yaw[euler_start_idx:euler_end_idx]
                    min_pitch = min(spike_pitch)
                    min_roll = min(spike_roll)
                    min_yaw = min(spike_yaw)
                    max_pitch = max(spike_pitch)
                    max_roll = max(spike_roll)
                    max_yaw = max(spike_yaw)
                    pitch_var = np.var(spike_pitch)
                    roll_var = np.var(spike_roll)
                    yaw_var = np.var(spike_yaw)

                    data.append([
                        spike["max_value"],
                        spike["min_value"],
                        # spike["max_value"] - spike["min_value"],
                        # max_y_value,
                        # min_y_value,
                        # max_y_value - min_y_value,
                        max_z_value,
                        # min_z_value,
                        # max_z_value - min_z_value,
                        spike["variance"],
                        # min_pitch,
                        # min_roll,
                        # min_yaw,
                        max_pitch - min_pitch,
                        max_roll,
                        # max_yaw,
                        # pitch_var,
                        # roll_var
                    ])
                    targets.append(i)

        # Create and fit a nearest-neighbor classifier
        self.model.fit(np.asarray(data), np.asarray(targets))

    def test_classifier(self, file_name):
        home = os.path.expanduser("~")
        sides = ["left", "right"]

        for side in sides:
            acc_file = pd.read_csv("%s/data/%s_acc_%s.csv" % (home, file_name, side))
            euler_file = pd.read_csv("%s/data/%s_euler_%s.csv" % (home, file_name, side))
            data_test = []

            # Build TimeSeries Objects
            acc_x_ts = TimeSeries(acc_file['time'], acc_file['x'])
            acc_y_ts = TimeSeries(acc_file['time'], acc_file['y'])
            acc_z_ts = TimeSeries(acc_file['time'], acc_file['z'])
            pitch = np.array(euler_file['pitch'])
            roll = np.array(euler_file['roll'])
            yaw = np.array(euler_file['yaw'])
            acc_times = np.array(acc_file['time'])
            euler_times = np.array(euler_file['time'])
            self.mod_euler_angles(pitch, roll, yaw)

            # Extract Spikes
            spikes_x = acc_x_ts.get_negative_spikes(config.TEST_THRESHOLD)
            for spike in spikes_x:
                max_y_value = max(acc_y_ts.data_axis[spike["start_index"]: spike["end_index"]])
                min_y_value = min(acc_y_ts.data_axis[spike["start_index"]: spike["end_index"]])

                max_z_value = max(acc_z_ts.data_axis[spike["start_index"]: spike["end_index"]])
                min_z_value = min(acc_z_ts.data_axis[spike["start_index"]: spike["end_index"]])

                euler_start_idx, euler_end_idx = self.find_euler_time(spike, acc_times, euler_times)
                spike_pitch = pitch[euler_start_idx:euler_end_idx]
                spike_roll = roll[euler_start_idx:euler_end_idx]
                spike_yaw = yaw[euler_start_idx:euler_end_idx]
                min_pitch = min(spike_pitch)
                min_roll = min(spike_roll)
                min_yaw = min(spike_yaw)
                max_pitch = max(spike_pitch)
                max_roll = max(spike_roll)
                max_yaw = max(spike_yaw)
                pitch_var = np.var(spike_pitch)
                roll_var = np.var(spike_roll)
                yaw_var = np.var(spike_yaw)

                data_test.append([
                    spike["max_value"],
                    spike["min_value"],
                    # spike["max_value"] - spike["min_value"],
                    # max_y_value,
                    # min_y_value,
                    # max_y_value - min_y_value,
                    max_z_value,
                    # min_z_value,
                    # max_z_value - min_z_value,
                    spike["variance"],
                    # min_pitch,
                    # min_roll,
                    # min_yaw,
                    max_pitch - min_pitch,
                    max_roll,
                    # max_yaw,
                    # pitch_var,
                    # roll_var
                ])

            predicted = self.model.predict(data_test)
            print side
            print predicted

    # Given a acceleration spike, find the corresponding range of a spike for euler angles
    def find_euler_time(self, spike, acc_times, euler_times):
        current_idx = 0
        start_time = acc_times[spike["start_index"]]
        end_time = acc_times[spike["end_index"]]

        while euler_times[current_idx] < start_time:
            current_idx += 1
        euler_start_idx = current_idx
        while euler_times[current_idx + 1] < end_time:
            current_idx += 1
        euler_end_idx = current_idx
        return euler_start_idx, euler_end_idx

    def get_abduction_angles(self, file_name):
        home = os.path.expanduser("~")
        jumps = []
        matched_jumps = []
        sides = ["left", "right"]

        left_acc_file = pd.read_csv("%s/data/%s_acc_left.csv" % (home, file_name))
        right_acc_file = pd.read_csv("%s/data/%s_acc_right.csv" % (home, file_name))
        left_spikes = (TimeSeries(left_acc_file['time'], left_acc_file['x'])).get_negative_spikes(config.TEST_THRESHOLD)
        right_spikes = (TimeSeries(right_acc_file['time'], right_acc_file['x'])).get_negative_spikes(config.TEST_THRESHOLD)

        for side in sides:
            acc_file = pd.read_csv("%s/data/%s_acc_%s.csv" % (home, file_name, side))
            euler_file = pd.read_csv("%s/data/%s_euler_%s.csv" % (home, file_name, side))
            data_test = []

            # Build TimeSeries Objects
            acc_x_ts = TimeSeries(acc_file['time'], acc_file['x'])
            acc_y_ts = TimeSeries(acc_file['time'], acc_file['y'])
            acc_z_ts = TimeSeries(acc_file['time'], acc_file['z'])

            # Get euler angles
            pitch = np.array(euler_file['pitch'])
            roll = np.array(euler_file['roll'])
            yaw = np.array(euler_file['yaw'])
            self.mod_euler_angles(pitch, roll, yaw)
            pitch_ts = TimeSeries(euler_file['time'], pd.Series(pitch))
            roll_ts = TimeSeries(euler_file['time'], pd.Series(roll))
            acc_times = np.array(acc_file['time'])
            euler_times = np.array(euler_file['time'])

            # Extract Spikes
            spikes = left_spikes if side == 'left' else right_spikes
            for spike in spikes:
                max_y_value = max(acc_y_ts.data_axis[spike["start_index"]: spike["end_index"]])
                min_y_value = min(acc_y_ts.data_axis[spike["start_index"]: spike["end_index"]])

                max_z_value = max(acc_z_ts.data_axis[spike["start_index"]: spike["end_index"]])
                min_z_value = min(acc_z_ts.data_axis[spike["start_index"]: spike["end_index"]])

                euler_start_idx, euler_end_idx = self.find_euler_time(spike, acc_times, euler_times)
                spike_pitch = pitch[euler_start_idx:euler_end_idx]
                spike_roll = roll[euler_start_idx:euler_end_idx]
                spike_yaw = yaw[euler_start_idx:euler_end_idx]
                min_pitch = min(spike_pitch)
                min_roll = min(spike_roll)
                min_yaw = min(spike_yaw)
                max_pitch = max(spike_pitch)
                max_roll = max(spike_roll)
                max_yaw = max(spike_yaw)
                pitch_var = np.var(spike_pitch)
                roll_var = np.var(spike_roll)
                yaw_var = np.var(spike_yaw)

                data_test.append([
                    spike["max_value"],
                    spike["min_value"],
                    # spike["max_value"] - spike["min_value"],
                    # max_y_value,
                    # min_y_value,
                    # max_y_value - min_y_value,
                    max_z_value,
                    # min_z_value,
                    # max_z_value - min_z_value,
                    spike["variance"],
                    # min_pitch,
                    # min_roll,
                    # min_yaw,
                    max_pitch - min_pitch,
                    max_roll,
                    # max_yaw,
                    # pitch_var,
                    # roll_var
                ])

            predictions = self.model.predict(data_test)
            if side == 'left':
                left_predictions = predictions
            else:
                right_predictions = predictions

            for idx, prediction in enumerate(predictions):
                # process a jump
                if prediction == 0:
                    euler_start_idx, euler_end_idx = self.find_euler_time(spikes[idx], acc_times, euler_times)
                    euler_start_angle = pitch[euler_start_idx]
                    euler_end_angle = pitch[euler_end_idx]
                    peak_angle = max(pitch[euler_start_idx:euler_end_idx]) if side == 'right' else min(pitch[euler_start_idx:euler_end_idx])
                    reference_angle = euler_end_angle if not spikes[idx]["left_stable"] and spikes[idx]["right_stable"] else euler_start_angle
                    abduction_angle = abs(peak_angle - reference_angle)

                    jump = {
                        "abduction_angle": abduction_angle,
                        "jump_time": spikes[idx]["time"],
                        "severity": self.get_severity(abduction_angle),
                        "jump_start_index": euler_start_idx,
                        "jump_end_index": euler_end_idx,
                        "leg": side
                    }
                    jumps.append(jump)

        for jump in jumps:
            match_found = False
            idx = 0
            while idx < len(jumps) and not match_found:
                if abs(jump["jump_time"] - jumps[idx]["jump_time"]) < 400 and not jump["jump_time"] == jumps[idx]["jump_time"]:
                    match_found = True
                    matched_jumps.append(jump)

                    euler_start_idx = jump["jump_start_index"]
                    euler_end_idx = jump["jump_end_index"]
                    plt.plot(jump["jump_time"], peak_angle, 'ro')
                    plt.plot(jump["jump_time"], reference_angle, 'go')
                    plt.plot(pitch_ts.time_axis[euler_start_idx:euler_end_idx],
                             pitch_ts.data_axis[euler_start_idx:euler_end_idx], '--r')
                idx += 1

        # plt.figure(figsize=(14, 7))
        # plt.plot(right_acc_file['time'], right_acc_file['x'], 'b')
        # plt.plot(left_acc_file['time'], left_acc_file['x'], 'c')
        # plt.title('left-right x')
        # for jump in matched_jumps:
        #     plt.plot(jump["jump_time"], 0, 'ro')
        # for jump in jumps:
        #     plt.plot(jump["jump_time"], 1, 'go')
        # plt.show()

        return matched_jumps

