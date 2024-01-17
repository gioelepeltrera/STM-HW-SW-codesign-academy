import pandas as pd
import numpy as np

def calculate_norms(df):
    df['acc_norm'] = df['A_X [mg]']**2 + df['A_Y [mg]']**2 + df['A_Z [mg]']**2
    df['gyro_norm'] = df['G_X [dps]']**2 + df['G_Y [dps]']**2 + df['G_Z [dps]']**2
    return df

def process_data(file_name, window_size=104, offset=1):
    data = pd.read_csv(file_name)
    all_means = []
    all_variances = []
    all_labels = []

    for start in range(0, len(data), offset):
        end = start + window_size
        if end > len(data):
            break

        window = data.iloc[start:end].copy()
        window_with_norms = calculate_norms(window)
        all_means.append(window_with_norms.mean())
        all_variances.append(window_with_norms.var())
        all_labels.append(window['LABEL'].mode()[0])  # Get the mode of the LABEL column

    # Merge means and variances
    means_df = pd.DataFrame(all_means)
    variances_df = pd.DataFrame(all_variances)

    # Merge means and variances, and keep only the desired columns
    result_df = pd.concat([means_df, variances_df.add_prefix('var_')], axis=1)
    selected_columns = ['A_X [mg]', 'A_Y [mg]','A_Z [mg]', 'G_X [dps]', 'G_Y [dps]', 'G_Z [dps]', 
                        'var_A_X [mg]', 'var_A_Y [mg]','var_A_Z [mg]', 'var_G_X [dps]', 'var_G_Y [dps]', 'var_G_Z [dps]',
                        'acc_norm', 'gyro_norm']
    result_df = result_df[selected_columns]

    # Add the most frequent label for each window
    result_df['LABEL'] = all_labels

    return result_df

# Example usage
file_name = './CompleteSet/CompleteData.csv'
result_df = process_data(file_name, offset=30)  # Adjust offset as needed

# Save to new CSV
result_df.to_csv('processed_data.csv', index=False)
