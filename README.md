# u-blox GNSS Driver for ROS2

A ROS2 Python node for reading position data from u-blox GNSS receivers connected via USB/serial and publishing it in real-time. The node only publishes new data when the position actually changes, avoiding unnecessary message spam.

## Features

- Reads NMEA sentences from u-blox GNSS receiver via USB serial connection
- Parses GGA sentences (position, altitude, time)
- Publishes `NavSatFix` messages to `/gnss/fix` topic
- Publishes altitude separately to `/gnss/altitude` topic
- Configurable position change threshold (default: 1e-6 degrees for lat/lon, 0.1m for altitude)
- Automatic reconnection if serial connection is lost
- Concurrent reading thread for non-blocking operation

## Hardware

- u-blox GNSS receiver (tested with GNSS receiver module)
- USB connection (usually appears as `/dev/ttyUSB0` on Linux)
- Default baud rate: 9600

## Installation

1. Build the package:
```bash
cd ~/unitree/ros2_ws
colcon build --packages-select ublox_gnss_driver
source install/setup.bash
```

2. Install required dependencies if not already installed:
```bash
sudo apt-get install python3-serial
pip install pyserial
```

## Usage

### Basic Launch

```bash
ros2 launch ublox_gnss_driver gnss.launch.py
```

### Custom Port and Baudrate

```bash
ros2 run ublox_gnss_driver gnss_node --ros-args -p port:=/dev/ttyUSB1 -p baudrate:=115200
```

### Monitor Output

```bash
ros2 topic echo /gnss/fix
ros2 topic echo /gnss/altitude
```

## Parameters

- `port` (str): Serial port device (default: `/dev/ttyUSB0`)
- `baudrate` (int): Serial baud rate (default: 9600)

## Published Topics

- `/gnss/fix` (sensor_msgs/NavSatFix): Position fix with latitude, longitude, altitude
- `/gnss/altitude` (std_msgs/Float64): Altitude in meters

## Notes

- The node parses standard NMEA GGA sentences
- If the GNSS receiver doesn't output GNSS sentences by default, configure it using u-blox software or AT commands
- Position change threshold can be tuned in the `gnss_node.py` file if needed
- The node runs in a separate thread for non-blocking serial reading
