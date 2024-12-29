import argparse
import time

import loguru
import psutil
import requests


def percent_to_azimuth(percent: float, half: bool = False) -> float:
    """ convert usage percentage to azimuth angle
    azimuth: 0 -> up, 90 -> right, 180 -> down, 270 -> left
    half: 0 -> left, 50 -> up, 100 -> right
    full: 0 -> left, 25 -> up, 50 -> right, 75 -> down, 100 -> left
    """
    if half:
        return (percent * 1.8 - 90 + 360) % 360
    else:
        return (percent * 3.6 - 90 + 360) % 360


def get_cpu_usage():
    return psutil.cpu_percent()


def get_memory_usage():
    return psutil.virtual_memory().percent


def main():
    while True:
        usage = get_cpu_usage() if args.monitor_type == "cpu" else get_memory_usage()
        azimuth = percent_to_azimuth(usage, half=args.half)
        loguru.logger.info(f"Usage: {usage}%, Azimuth: {azimuth}deg")
        try:
            resp = requests.post(f"http://{args.compass_ip}/setAzimuth?azimuth={azimuth}")
            loguru.logger.debug(f"Status: {resp.status_code}")
        except Exception as e:
            loguru.logger.error(f"Error: {e}")
        time.sleep(args.interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCompass System Monitor")
    parser.add_argument("--compass-ip", type=str, required=True, help="IP address of the MCompass")
    parser.add_argument("--monitor-type", type=str, default="cpu", help="Monitor type: cpu/mem")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval between each update")
    parser.add_argument("--half", type=bool, default=True, help="Half circle mode")
    parser.add_argument("--silent", type=bool, default=False, help="Silent mode")
    args = parser.parse_args()
    if args.silent:
        loguru.logger.remove()
    main()
