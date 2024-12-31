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


def get_usage(typ: str) -> float:
    if typ == "cpu":
        return psutil.cpu_percent()
    elif typ == "mem":
        return psutil.virtual_memory().percent
    else:
        loguru.logger.error("Invalid monitor type")
        return 0.0


def set_azimuth(azimuth: float) -> None:
    try:
        resp = requests.post(f"http://{args.compass_ip}/setAzimuth?azimuth={azimuth}", timeout=0.5)
        loguru.logger.info(f"Status: {resp.status_code}")
    except Exception as e:
        loguru.logger.error(f"Error: {e}")


def set_azimuth_with_animation(cur_azimuth: float, tgt_azimuth: float, diff: int) -> None:
    cur_azimuth = (cur_azimuth + 90) % 360
    tgt_azimuth = (tgt_azimuth + 90) % 360

    while cur_azimuth != tgt_azimuth:
        if cur_azimuth < tgt_azimuth:
            cur_azimuth = min(cur_azimuth + diff, tgt_azimuth)
        else:
            cur_azimuth = max(cur_azimuth - diff, tgt_azimuth)
        set_azimuth((cur_azimuth - 90 + 360) % 360)


def main(args: argparse.Namespace) -> None:
    cur_azimuth = 0.0
    while True:
        start_time = time.time()

        usage = get_usage(args.monitor_type)
        azimuth = percent_to_azimuth(usage, half=args.half, log=args.logarithm)
        loguru.logger.info(f"Usage: {usage}%, Azimuth: {azimuth}°")

        if args.animation == 0:
            set_azimuth(azimuth)
        else:
            set_azimuth_with_animation(cur_azimuth, azimuth, args.animation)
            cur_azimuth = azimuth

        elapsed_time = time.time() - start_time
        time.sleep(max(0, args.interval - elapsed_time))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCompass System Monitor")
    parser.add_argument("--compass-ip", type=str, default="", help="IP address of the MCompass")
    parser.add_argument("--monitor-type", type=str, default="cpu", help="Monitor type: cpu/mem")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval between each update")
    parser.add_argument("--silent", action='store_true', help="Silent mode")
    parser.add_argument("--half", action='store_true', help="Half circle mode")
    parser.add_argument("--logarithm", action='store_true', help="Logarithmic curve mode")
    parser.add_argument("--animation", type=int, default=0, help="Animation interpolation degree, 0 for no animation")
    args = parser.parse_args()
    if args.silent:
        loguru.logger.remove()
    if args.compass_ip == "":
        loguru.logger.warning("IP address of the MCompass is not provided in the argument, receive it from stdin")
        args.compass_ip = input("Enter the IP address of the MCompass: ")
    main(args)
