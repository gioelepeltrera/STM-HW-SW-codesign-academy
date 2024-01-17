import csv

# Constants (to be adjusted as per the actual values)
ACC_SENS = 0.244
GYR_SENS = 0.07
WIN_LEN_IN_SAMPLES = 104

# Global Variables
win_count = 0
acc_norm_sqred = 0.0
gyro_norm_sqred = 0.0
a_x_k = 0.0
a_x_ex = 0.0
a_x_ex2 = 0.0

def reset_status():
    global win_count, gyro_norm_sqred, acc_norm_sqred, a_x_k, a_x_ex, a_x_ex2
    win_count = 0
    gyro_norm_sqred = 0.0
    acc_norm_sqred = 0.0
    a_x_k = 0.0
    a_x_ex = 0.0
    a_x_ex2 = 0.0

def algo_00(a_x, a_y, a_z, g_x, g_y, g_z):
    global win_count, acc_norm_sqred, gyro_norm_sqred, a_x_k, a_x_ex, a_x_ex2
    # ... Rest of the algorithm ...
    a_norm_sqred = a_x * a_x + a_y * a_y + a_z * a_z
    g_norm_sqred = g_x * g_x + g_y * g_y + g_z * g_z
    win_count += 1
    acc_norm_sqred  += (a_norm_sqred - acc_norm_sqred) / win_count
    gyro_norm_sqred += (g_norm_sqred - gyro_norm_sqred) / win_count

    if win_count == 1:
        a_x_k = a_x

    a_x_ex += a_x - a_x_k
    a_x_ex2 += (a_x - a_x_k) * (a_x - a_x_k)

    prediction = 0

    if win_count == WIN_LEN_IN_SAMPLES:
	
        var_a_x = (a_x_ex2 - (a_x_ex * a_x_ex) / win_count) / (win_count - 1)

        if acc_norm_sqred <= 3085268.25:
            if gyro_norm_sqred <= 6889.0322:
                if var_a_x <= 6461.0833:
                    prediction = 1
                else:
                    prediction = 4
            else:
                prediction = 2
        else:
            prediction = 3

        reset_status()
        return prediction
	

def read_csv_and_process(file_name):
    with open(file_name, 'r') as file:
        csv_reader = csv.reader(file)
        i = 0
        correct = 0
        for row in csv_reader:
            # Assuming the CSV has columns: a_x, a_y, a_z, g_x, g_y, g_z
            a_x, a_y, a_z, g_x, g_y, g_z, LABEL = map(float, row)
            prediction = algo_00(a_x, a_y, a_z, g_x, g_y, g_z)
            i += 1
            if prediction == LABEL:
                correct += 1
        
        print(f'Accuracy: {correct / i * 100}%')

# Example usage
read_csv_and_process('../test_set/tot_test.csv')
