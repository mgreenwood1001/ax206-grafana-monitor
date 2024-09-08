import subprocess
import json
import time
from prometheus_client import start_http_server, Gauge

# Create Prometheus gauges
temperature_gauge = Gauge('system_temperature_celsius', 'Temperature in Celsius', ['sensor', 'label'])
voltage_gauge = Gauge('system_voltage_volts', 'Voltage in Volts', ['sensor', 'label'])
power_gauge = Gauge('system_power_watts', 'Power consumption in Watts', ['sensor', 'label'])
uptime_gauge = Gauge('system_uptime_seconds', 'System uptime in seconds')
load_average_gauge = Gauge('system_load_average', 'System load average', ['load'])


def get_sensors_data():
    try:
        result = subprocess.run(['sensors', '-j'], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running sensors command: {e}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON data: {e}")
        return {}


def get_system_uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            return uptime_seconds
    except IOError as e:
        print(f"Error reading /proc/uptime: {e}")
        return 0.0


def get_load_averages():
    try:
        with open('/proc/loadavg', 'r') as f:
            load_avg = f.readline().split()
            return [float(avg) for avg in load_avg[:3]]
    except IOError as e:
        print(f"Error reading /proc/loadavg: {e}")
        return [0.0, 0.0, 0.0]


def parse_and_set_metrics(data):
    for sensor, values in data.items():
        if 'temp1_input' in values.get('temp1', {}):
            temperature_gauge.labels(sensor=sensor, label='temp1').set(values['temp1']['temp1_input'])
        if 'edge' in values and 'temp1_input' in values['edge']:
            temperature_gauge.labels(sensor=sensor, label='edge').set(values['edge']['temp1_input'])
        if 'Composite' in values:
            if 'temp1_input' in values['Composite']:
                temperature_gauge.labels(sensor=sensor, label='composite').set(values['Composite']['temp1_input'])
            if 'temp2_input' in values.get('Sensor 1', {}):
                temperature_gauge.labels(sensor=sensor, label='sensor1').set(values['Sensor 1']['temp2_input'])
            if 'temp3_input' in values.get('Sensor 2', {}):
                temperature_gauge.labels(sensor=sensor, label='sensor2').set(values['Sensor 2']['temp3_input'])
        if 'vddgfx' in values and 'in0_input' in values['vddgfx']:
            voltage_gauge.labels(sensor=sensor, label='vddgfx').set(values['vddgfx']['in0_input'])
        if 'vddnb' in values and 'in1_input' in values['vddnb']:
            voltage_gauge.labels(sensor=sensor, label='vddnb').set(values['vddnb']['in1_input'])
        if 'PPT' in values and 'power1_input' in values['PPT']:
            power_gauge.labels(sensor=sensor, label='ppt').set(values['PPT']['power1_input'])


if __name__ == "__main__":
    start_http_server(9191)  # Start HTTP server on port 8000
    while True:
        sensors_data = get_sensors_data()
        if sensors_data:
            parse_and_set_metrics(sensors_data)

        # Update uptime and load average metrics
        uptime_seconds = get_system_uptime()
        uptime_gauge.set(uptime_seconds)

        load_averages = get_load_averages()
        load_average_gauge.labels(load='1min').set(load_averages[0])
        load_average_gauge.labels(load='5min').set(load_averages[1])
        load_average_gauge.labels(load='15min').set(load_averages[2])

        time.sleep(10)  # qUpdate metrics every 10 seconds
