import argparse
import time
import json
import os
from datetime import datetime, timedelta, timezone
import tzlocal  # to get the local timezone
from labjack import ljm


def average_channels_from_config(handle, config_file):
    """
    Averages multiple analog input channels using settings from a JSON configuration file.
    Applies a slope and offset for unit conversion to each channel.
    Uses human-readable labels for CSV headers if provided.
    Dynamically updates the log filename based on the current date.
    """
    # Load configuration
    with open(config_file, 'r') as f:
        config = json.load(f)

    channels = config["channels"]
    slopes = config["slopes"]
    offsets = config["offsets"]
    labels = config.get("labels", {})  # Default to empty dict if labels are not provided
    sampling_rate = config.get("sampling_rate", 2.0)
    averaging_period = config.get("averaging_period", 15)

    # Reduce the actual averaging time by 1 second to account for processing time
    actual_averaging_time = averaging_period - 1

    # Use channel names as fallback labels
    field_labels = [labels.get(channel, channel) for channel in channels]

    aNames = channels
    aWrites = [ljm.constants.READ] * len(channels)
    aNumValues = [1] * len(channels)
    aValues = [0] * len(channels)

    project_name = config.get("project_name", "Channel_Averages")
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_filename = f"{project_name}_{current_date}.csv"

    print(f"Starting logging with initial file: {log_filename}")
    print(f"Sampling Rate: {sampling_rate} Hz")
    print(f"Averaging Period: {averaging_period} seconds (Actual Averaging Time: {actual_averaging_time} seconds)")
    print("Timestamps are in ISO8601 format.")

    try:
        # Align to the next multiple of the averaging_period
        current_time = datetime.now()
        seconds_since_minute = current_time.second + current_time.microsecond / 1e6
        wait_time = (averaging_period - (seconds_since_minute % averaging_period)) % averaging_period
        print(f"Waiting {wait_time:.2f} seconds to align with the next {averaging_period}-second interval.")
        time.sleep(wait_time)

        log_file = None  # Initialize log file handler

        # Set the next target time to align with the current time
        next_target_time = datetime.now().replace(microsecond=0) + timedelta(seconds=averaging_period)

        # Get the local timezone
        local_tz = tzlocal.get_localzone()

        while True:
            # Determine the current date and log filename
            current_date = datetime.now().strftime("%Y-%m-%d")
            new_log_filename = f"{project_name}_{current_date}.csv"

            # Check if we need to switch to a new log file
            if log_file is None or new_log_filename != log_filename:
                log_filename = new_log_filename
                if log_file:
                    log_file.close()  # Close the previous file
                file_exists = os.path.exists(log_filename)
                log_file = open(log_filename, 'a')

                # Write the header if this is a new file
                if not file_exists:
                    header = "time," + ",".join(field_labels) + "\n"
                    log_file.write(header)

                print(f"Logging to file: {log_filename}")

            # Record the start time of this averaging period
            start_timestamp = next_target_time.astimezone(local_tz).isoformat()

            sums = {channel: 0.0 for channel in channels}
            counts = {channel: 0 for channel in channels}
            end_time = next_target_time + timedelta(seconds=actual_averaging_time)

            # Perform averaging by sampling the input channels
            while datetime.now() < end_time:
                results = ljm.eNames(handle, len(aNames), aNames, aWrites, aNumValues, aValues)
                for i, channel in enumerate(channels):
                    sums[channel] += results[i]
                    counts[channel] += 1
                time.sleep(1.0 / sampling_rate)  # Sleep to maintain sampling rate

            # Calculate averages, apply slopes and offsets
            averages = {
                channel: (sums[channel] / counts[channel] * slopes[channel] + offsets[channel] if counts[channel] > 0 else 0)
                for channel in channels
            }

            # Write the averages to the CSV file
            values = ",".join(f"{averages[channel]:.6f}" for channel in channels)
            log_entry = f"{start_timestamp},{values}\n"
            log_file.write(log_entry)
            log_file.flush()  # Ensure data is written to disk
            print(f"Logged averages at {start_timestamp}: {values}")

            # Calculate the next target time to maintain a consistent schedule
            next_target_time += timedelta(seconds=averaging_period)
            now = datetime.now()
            sleep_time = (next_target_time - now).total_seconds()

            # Sleep until the start of the next averaging period
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nData acquisition stopped by user.")
    except Exception as e:
        print(f"An error occurred during data acquisition: {e}")
    finally:
        if log_file:
            log_file.close()  # Ensure the log file is closed properly


def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="LabJack Data Acquisition Tool with Configurable Inputs")
    parser.add_argument('--config', type=str, required=True, help='Path to the JSON configuration file.')
    args = parser.parse_args()

    # Load configuration
    with open(args.config, 'r') as f:
        config = json.load(f)

    # Extract serial number from the configuration, if specified
    serial_number = config.get("serial_number", "ANY")
    device_type = "ANY"  # Compatible with any LJM device

    print(f"Attempting to connect to LabJack {device_type} with serial number: {serial_number}")

    # Open LabJack device
    try:
        handle = ljm.openS(device_type, "ANY", serial_number)  # Use specified serial number or "ANY"
    except ljm.LJMError as e:
        print(f"Failed to open LabJack {device_type} with serial number {serial_number}: {e}")
        if serial_number != "ANY":
            print("Retrying with ANY identifier...")
            try:
                handle = ljm.openS(device_type, "ANY", "ANY")  # Fall back to "ANY"
            except ljm.LJMError as e2:
                print(f"Failed to open LabJack {device_type} with ANY identifier: {e2}")
                return
        else:
            return

    # Use configuration file for settings
    average_channels_from_config(handle, args.config)

    # Close handle
    ljm.close(handle)


if __name__ == "__main__":
    main()

