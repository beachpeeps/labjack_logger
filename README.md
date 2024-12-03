# LabJack T-series Data Acquisition Tool

This program is designed to collect and log data from a LabJack T-series device. It allows for configurable data acquisition using various analog input channels, applying optional scaling and offsets. The program also supports time-stamped logging in ISO 8601 format, with the computer's local timezone automatically detected and used in the logged data.

## Features
- Connects to a LabJack T-series device using a specified serial number or automatically detects available devices.
- Supports averaging data over configurable periods.
- Applies configurable slopes and offsets to each input channel for unit conversion.
- Logs data in CSV format with a header that includes time and channel labels.
- Automatically switches log files at midnight to ensure data is organized by day.
- Ensures accurate timing by averaging for one second less than the configured interval, allowing time for data processing and writing.
- Uses the computer's local timezone for ISO 8601 timestamps.

## Requirements
- Python 3
- LabJackM library (`labjack.ljm`). Instructions for installation can be found [here](https://support.labjack.com/docs/ljm-software-installer-downloads-t4-t7-t8-digit). After installing LJM, use the following command to install the Python wrapper:
  ```sh
  pip install labjack-ljm
  ```
- `tzlocal` library for local timezone detection

To install the required Python dependencies, run:

```sh
pip install tzlocal
```

## Configuration File
The program uses a JSON configuration file to define its settings. Below is an example configuration file (`config.json`):

```json
{
    "project_name": "MyLabjackProject",
    "serial_number": "123456789",
    "channels": ["AIN0", "AIN1", "AIN2", "TEMPERATURE_DEVICE_K"],
    "slopes": {
        "AIN0": 100.0,
        "AIN1": 200.0,
        "AIN2": 50.0,
        "TEMPERATURE_DEVICE_K": 1.0
    },
    "offsets": {
        "AIN0": 5.0,
        "AIN1": 10.0,
        "AIN2": 0.0,
        "TEMPERATURE_DEVICE_K": -273.15
    },
    "labels": {
        "AIN0": "Current",
        "AIN1": "Voltage",
        "AIN2": "Temperature",
        "TEMPERATURE_DEVICE_K": "InternalTemperatureC"
    },
    "sampling_rate": 2.0,
    "averaging_period": 15
}
```

### Configuration Fields
- **`project_name`**: Optional. A project name. If not specified, the program will use Channel_Averages.
- **`serial_number`**: Optional. The serial number of the LabJack device. If not specified, the program will connect to any available device.
- **`channels`**: A list of analog input channels to record (e.g., `AIN0`, `AIN1`).
- **`slopes`**: A dictionary of slopes for unit conversion, applied to each channel.
- **`offsets`**: A dictionary of offsets for unit conversion, applied to each channel.
- **`labels`**: A dictionary of human-readable labels for each channel, used in the CSV header.
- **`sampling_rate`**: The rate at which data is sampled, in Hertz.
- **`averaging_period`**: The period over which data is averaged, in seconds. The program will average for one second less than this value to allow time for processing.

## Usage
To run the program, use the following command:

```sh
python labjack_monitor.py --config config.json
```

### Command-Line Arguments
- **`--config`**: Path to the JSON configuration file.

### Example
```sh
python labjack_monitor.py --config config.json
```

This command will start the data acquisition using the settings specified in `config.json`.

## Output
The program logs data to a CSV file named `Channel_Averages_YYYY-MM-DD.csv`, where `YYYY-MM-DD` represents the current date. Each log entry includes:
- **`time`**: The timestamp in ISO 8601 format, reflecting the local timezone.
- **Channel values**: The averaged values for each channel, as specified in the configuration.

### Example CSV Output
```
time,Current,Voltage,Temperature
2024-11-30T05:13:00-08:00,7.345600,16.913400,1.234500
2024-11-30T05:13:15-08:00,7.456700,17.123400,1.345600
...
```

## Notes
- The program aligns to the next multiple of the averaging period before starting data collection, ensuring consistent intervals.
- The timestamp format includes the local timezone offset (e.g., `-08:00` for PST).
- The program will automatically switch to a new log file at midnight to keep the data organized by day.

## Handling Device Connections
If a specific serial number is provided in the configuration but the program fails to connect to that device, it will fall back to connecting to any available LabJack T-series device.

## Stopping the Program
To stop the data acquisition, press `Ctrl+C`. The program will gracefully stop and ensure all data is written to the log file.

## License
This program is licensed under the MIT License.

## Author
This tool was developed to facilitate data acquisition using LabJack T-series devices, ensuring precise timing and user-friendly configuration options.

## Troubleshooting
- **Failed to Connect to Device**: If the program cannot connect to the specified LabJack device, ensure that the device is properly connected and the serial number in the configuration file is correct. The program will attempt to connect to any available device if the specified one is not found.
- **Missing Dependencies**: If you encounter import errors, make sure that all required Python packages are installed (`labjack.ljm` and `tzlocal`). Use `pip install tzlocal` to install the missing dependencies.
- **Incorrect Timestamps**: If the timestamps do not reflect the correct timezone, make sure that the system's timezone settings are correctly configured. The program uses the local timezone detected from the system.
- **Permission Issues**: If you face permission issues while accessing the LabJack device, ensure that you have the appropriate permissions to interact with the USB device on your system.


