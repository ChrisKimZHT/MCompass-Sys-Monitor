import argparse
import time

import loguru
import psutil
import requests


def percent_to_azimuth(percent: float, half: bool = False, log: bool = False) -> float:
    """convert usage percentage to azimuth angle
    azimuth : 0 -> up, 90 -> right, 180 -> down, 270 -> left
    ------
    half: 1.8deg/pct, 0 -> left, 50 -> up, 100 -> right
    full: 3.6deg/pct, 0 -> left, 25 -> up, 50  -> right, 75 -> down, 100 -> left
    ------
    half log: 0~10 ->   9deg/pct, 10~30 ->  4.5deg/pct, 30~60 ->   3deg/pct, 60~100 ->  2.25deg/pct
    full log: 0~10 -> 4.5deg/pct, 10~30 -> 2.25deg/pct, 30~60 -> 1.5deg/pct, 60~100 -> 1.125deg/pct
    """
    pct_list = [10, 20, 30, 40]
    if half == True and log == False:
        deg_list = [1.8, 1.8, 1.8, 1.8]
    elif half == False and log == False:
        deg_list = [3.6, 3.6, 3.6, 3.6]
    elif half == True and log == True:
        deg_list = [4.5, 2.25, 1.5, 1.125]
    else:  # half == False and log == True
        deg_list = [9, 4.5, 3, 2.25]
    azimuth = 0.0
    for i in range(4):
        azimuth += deg_list[i] * min(percent, pct_list[i])
        percent -= pct_list[i]
        if percent <= 0.0:
            break
    azimuth = (azimuth - 90 + 360) % 360
    return azimuth


def get_cpu_usage():
    return psutil.cpu_percent()


def get_memory_usage():
    return psutil.virtual_memory().percent


def main():
    while True:
        usage = get_cpu_usage() if args.monitor_type == "cpu" else get_memory_usage()
        azimuth = percent_to_azimuth(usage, half=args.half, log=args.logarithm)
        try:
            resp = requests.post(f"http://{args.compass_ip}/setAzimuth?azimuth={azimuth}", timeout=0.5)
            loguru.logger.info(f"Usage: {usage}%, Azimuth: {azimuth}°, Status: {resp.status_code}")
        except Exception as e:
            loguru.logger.error(f"Usage: {usage}%, Azimuth: {azimuth}°, Error: {e}")
        time.sleep(args.interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCompass System Monitor")
    parser.add_argument("--compass-ip", type=str, required=True, help="IP address of the MCompass")
    parser.add_argument("--monitor-type", type=str, default="cpu", help="Monitor type: cpu/mem")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval between each update")
    parser.add_argument("--silent", action='store_true', help="Silent mode")
    parser.add_argument("--half", action='store_true', help="Half circle mode")
    parser.add_argument("--logarithm", action='store_true', help="Logarithmic curve mode")
    args = parser.parse_args()
    if args.silent:
        loguru.logger.remove()
    main()
