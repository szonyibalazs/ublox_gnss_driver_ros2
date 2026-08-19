#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix
from std_msgs.msg import Float64
import serial
import threading
from typing import Optional, Tuple


class UbloxGNSSNode(Node):
    def __init__(self):
        super().__init__('ublox_gnss_node')

        self.declare_parameter('port', '/dev/ttyACM0')
        self.declare_parameter('baudrate', 9600)

        self.port = self.get_parameter('port').value
        self.baudrate = self.get_parameter('baudrate').value

        self.get_logger().info(f'Initializing u-blox GNSS on {self.port} @ {self.baudrate} baud')

        self.publisher = self.create_publisher(NavSatFix, '/gnss/fix', 10)
        self.altitude_publisher = self.create_publisher(Float64, '/gnss/altitude', 10)

        self.serial_port: Optional[serial.Serial] = None
        self.last_position: Optional[Tuple[float, float, float]] = None

        self.position_change_threshold = 1e-6
        self.running = True

        self.connect_serial()

        self.read_thread = threading.Thread(target=self.read_loop, daemon=True)
        self.read_thread.start()

    def connect_serial(self) -> bool:
        try:
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1.0,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            self.get_logger().info(f'Connected to {self.port}')
            return True
        except serial.SerialException as e:
            self.get_logger().error(f'Failed to open serial port: {e}')
            return False

    def parse_nmea_gga(self, sentence: str) -> Optional[Tuple[float, float, float]]:
        try:
            parts = sentence.split(',')
            if len(parts) < 10:
                return None

            if parts[2] == '' or parts[4] == '':
                return None

            try:
                lat_str = parts[2]
                lat_dir = parts[3]
                lon_str = parts[4]
                lon_dir = parts[5]
                alt_str = parts[9]

                lat_deg = int(lat_str[:2])
                lat_min = float(lat_str[2:])
                latitude = lat_deg + lat_min / 60.0
                if lat_dir == 'S':
                    latitude = -latitude

                lon_deg = int(lon_str[:3])
                lon_min = float(lon_str[3:])
                longitude = lon_deg + lon_min / 60.0
                if lon_dir == 'W':
                    longitude = -longitude

                altitude = float(alt_str) if alt_str else 0.0

                return (latitude, longitude, altitude)
            except (ValueError, IndexError):
                return None
        except Exception as e:
            self.get_logger().debug(f'Error parsing NMEA GGA: {e}')
            return None

    def read_loop(self):
        while self.running:
            if self.serial_port is None or not self.serial_port.is_open:
                if not self.connect_serial():
                    threading.Event().wait(2.0)
                    continue

            try:
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()

                    if line.startswith('$GPGGA') or line.startswith('$GNGGA'):
                        position = self.parse_nmea_gga(line[6:])

                        if position and self.position_changed(position):
                            self.last_position = position
                            self.publish_position(position)
                else:
                    threading.Event().wait(0.1)
            except serial.SerialException as e:
                self.get_logger().error(f'Serial read error: {e}')
                self.serial_port = None
            except Exception as e:
                self.get_logger().error(f'Unexpected error: {e}')

    def position_changed(self, new_position: Tuple[float, float, float]) -> bool:
        if self.last_position is None:
            return True

        lat_diff = abs(new_position[0] - self.last_position[0])
        lon_diff = abs(new_position[1] - self.last_position[1])
        alt_diff = abs(new_position[2] - self.last_position[2])

        return (lat_diff > self.position_change_threshold or
                lon_diff > self.position_change_threshold or
                alt_diff > 0.1)

    def publish_position(self, position: Tuple[float, float, float]):
        latitude, longitude, altitude = position

        msg = NavSatFix()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'gnss'
        msg.latitude = latitude
        msg.longitude = longitude
        msg.altitude = altitude
        msg.position_covariance_type = NavSatFix.COVARIANCE_TYPE_UNKNOWN

        self.publisher.publish(msg)

        alt_msg = Float64()
        alt_msg.data = altitude
        self.altitude_publisher.publish(alt_msg)

        self.get_logger().debug(
            f'Published position: lat={latitude:.6f}, lon={longitude:.6f}, alt={altitude:.2f}m'
        )

    def destroy_node(self):
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = UbloxGNSSNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
