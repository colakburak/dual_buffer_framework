from dual_buffer import DualBufferSystem

# -- Example Proccess Data Function --
def process_sensor_data(data_buffer):
    """
    Process data buffer and check each data point for anomalies.
    """
    print("Processing data buffer...")
    for data_point in data_buffer:
        if is_anomalous(data_point):
            alert_system(data_point)

def is_anomalous(data_point):
    """
    Determine if a data point is anomalous.
    """
    # Print the data point for testing and debugging
    print(f"Checking if data point is anomalous: {data_point}")

    # Define a threshold for anomaly detection
    threshold_value = 0.8  # Example threshold, adjust as needed

    # Assuming data_point is a dictionary and we are interested in a 'sensor_value'
    sensor_value = data_point.get('sensor_value', 0)

    # Check if the sensor value exceeds the threshold
    is_anomaly = sensor_value > threshold_value

    # For testing, print whether the data point is anomalous
    if is_anomaly:
        print(f"Anomaly detected: {data_point}")
    else:
        print(f"Data point is normal: {data_point}")

    return is_anomaly


def alert_system(data_point):
    """
    Alert system for anomalous data points.
    """
    # Print an alert message for testing
    print(f"Anomaly detected: {data_point}")



def main():
    window_size = 100
    dual_buffer_system = DualBufferSystem(window_size, process_sensor_data)
    dual_buffer_system.start()


if __name__ == "__main__":
    main()