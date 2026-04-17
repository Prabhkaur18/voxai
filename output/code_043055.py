import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler

def normalize_data(data, normalization_type='min_max'):
    """
    Normalize the given data using the specified normalization type.

    Args:
    - data (numpy array or pandas DataFrame): The data to be normalized.
    - normalization_type (str, optional): The type of normalization to use. Defaults to 'min_max'.
        - 'min_max': Min-Max normalization (also known as normalization to [0, 1] range)
        - 'z_score': Z-score normalization (also known as standardization)
        - 'log': Log normalization

    Returns:
    - normalized_data (numpy array or pandas DataFrame): The normalized data.
    """
    if normalization_type == 'min_max':
        # Create a MinMaxScaler object
        scaler = MinMaxScaler()
        # Fit the scaler to the data and transform the data
        normalized_data = scaler.fit_transform(data)
    elif normalization_type == 'z_score':
        # Create a StandardScaler object
        scaler = StandardScaler()
        # Fit the scaler to the data and transform the data
        normalized_data = scaler.fit_transform(data)
    elif normalization_type == 'log':
        # Calculate the logarithm of the data
        normalized_data = np.log(data)
        # Avoid division by zero error
        normalized_data[np.isinf(normalized_data)] = 0
    else:
        raise ValueError("Invalid normalization type")

    return normalized_data

# Example usage:
if __name__ == "__main__":
    # Create a sample dataset
    data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

    # Normalize the data using Min-Max normalization
    min_max_normalized_data = normalize_data(data, normalization_type='min_max')
    print("Min-Max normalized data:")
    print(min_max_normalized_data)

    # Normalize the data using Z-score normalization
    z_score_normalized_data = normalize_data(data, normalization_type='z_score')
    print("\nZ-score normalized data:")
    print(z_score_normalized_data)

    # Normalize the data using log normalization
    log_normalized_data = normalize_data(data, normalization_type='log')
    print("\nLog normalized data:")
    print(log_normalized_data)