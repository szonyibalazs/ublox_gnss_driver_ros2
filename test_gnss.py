#!/usr/bin/env python3
"""
Simple script to test GNSS connection without ROS2.
Useful for debugging serial communication with the u-blox receiver.
"""

import serial
import sys
from pathlib import Path


def test_gnss_connection(port='/dev/ttyUSB0', baudrate=9600):
    """Test basic connection to GNSS receiver and display raw data."""
    print(f'Attempting to connect to {port} at {baudrate} baud...')

    try:
        ser = serial.Serial(port=port, baudrate=baudrate, timeout=2.0)
        print(f'✓ Successfully opened {port}')
    except serial.SerialException as e:
        print(f'✗ Failed to open serial port: {e}')
        print('\nAvailable ports:')
        import glob
        ports = glob.glob('/dev/tty*USB*') + glob.glob('/dev/ttyS*')
        if ports:
            for p in ports:
                print(f'  - {p}')
        else:
            print('  No serial devices found. Check connection.')
        return False

    print('\nReading data (Ctrl+C to stop)...\n')
    print('=' * 80)

    try:
        line_count = 0
        gga_count = 0
        error_count = 0

        while True:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        line_count += 1
                        print(line)

                        if line.startswith('$GPGGA') or line.startswith('$GNGGA'):
                            gga_count += 1
                            parts = line.split(',')
                            if len(parts) > 2 and parts[2]:
                                print(f'  → Position found: lat={parts[2]}, lon={parts[4]}')
                except Exception as e:
                    error_count += 1
                    print(f'Parse error: {e}')
    except KeyboardInterrupt:
        print('\n' + '=' * 80)
        print(f'\nStatistics:')
        print(f'  Lines read: {line_count}')
        print(f'  GGA sentences: {gga_count}')
        print(f'  Parse errors: {error_count}')
    finally:
        ser.close()
        print(f'\n✓ Connection closed')


if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baudrate = int(sys.argv[2]) if len(sys.argv) > 2 else 9600
    test_gnss_connection(port, baudrate)
