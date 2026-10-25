
import argparse
import csv
import platform
import re
import socket
import statistics
import subprocess
import time
from datetime import datetime
from pathlib import Path


# Project directories
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "raw"


def get_target_ip(target):
    """Resolve the target hostname to an IPv4 address."""
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        return ""


def run_ping(target, count):
    """Run the system ping command and return RTT values and raw output."""
    system = platform.system()

    if system == "Windows":
        command = [
            "ping", "-n", str(count), "-w", "1000", target
        ]
    else:
        command = [
            "ping", "-n", "-c", str(count), "-W", "1", target
        ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=count * 2 + 5
        )
        output = result.stdout + "\n" + result.stderr
    except (subprocess.TimeoutExpired, OSError) as error:
        return [], str(error)

    # Extract response times, including values such as time<1ms.
    rtt_values = []

    pattern = r"time\s*[=<]\s*(\d+(?:[.,]\d+)?)\s*ms"

    for match in re.finditer(pattern, output, re.IGNORECASE):
        rtt = float(match.group(1).replace(",", "."))
        if "<" in match.group(0):
            rtt /= 2
        rtt_values.append(rtt)

    return rtt_values, output


def main():
    parser = argparse.ArgumentParser(
        description="Measure network RTT and packet loss."
    )

    parser.add_argument("--target", default="spotify.com")
    parser.add_argument("--duration", type=int, default=60,
                        help="Measurement duration in seconds")
    parser.add_argument("--interval", type=int, default=10,
                        help="Interval between ping series in seconds")
    parser.add_argument("--count", type=int, default=3,
                        help="Packets per ping series")
    parser.add_argument("--location", default="home")
    parser.add_argument("--network", default="wifi")

    args = parser.parse_args()

    if args.duration < 1 or args.interval < 1 or args.count < 1:
        parser.error("Duration, interval and count must be positive.")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = DATA_DIR / f"ping_{session_id}.csv"

    target_ip = get_target_ip(args.target)
    start_time = time.monotonic()
    next_measurement = start_time
    series_number = 0

    columns = [
        "session_id", "series_number", "timestamp",
        "target", "target_ip", "location", "network",
        "packets_sent", "packets_received", "packet_loss_percent",
        "rtt_min_ms", "rtt_median_ms", "rtt_mean_ms", "rtt_max_ms"
    ]

    print(f"Target: {args.target} ({target_ip or 'IP unresolved'})")
    print(f"Duration: {args.duration}s | Interval: {args.interval}s")
    print(f"Results: {output_file}")
    print("Press Ctrl+C to stop early.\n")

    try:
        with output_file.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=columns)
            writer.writeheader()
            csv_file.flush()

            while time.monotonic() - start_time < args.duration:
                delay = next_measurement - time.monotonic()

                if delay > 0:
                    time.sleep(delay)

                if time.monotonic() - start_time >= args.duration:
                    break

                series_number += 1
                timestamp = datetime.now().astimezone().isoformat(
                    timespec="seconds"
                )

                rtts, raw_output = run_ping(args.target, args.count)
                received = len(rtts)
                packet_loss = 100 * (args.count - received) / args.count

                row = {
                    "session_id": session_id,
                    "series_number": series_number,
                    "timestamp": timestamp,
                    "target": args.target,
                    "target_ip": target_ip,
                    "location": args.location,
                    "network": args.network,
                    "packets_sent": args.count,
                    "packets_received": received,
                    "packet_loss_percent": round(packet_loss, 2),
                    "rtt_min_ms": min(rtts) if rtts else "",
                    "rtt_median_ms": statistics.median(rtts) if rtts else "",
                    "rtt_mean_ms": round(statistics.mean(rtts), 2) if rtts else "",
                    "rtt_max_ms": max(rtts) if rtts else "",
                }

                writer.writerow(row)
                csv_file.flush()

                if rtts:
                    print(
                        f"[{timestamp}] Series {series_number}: "
                        f"median RTT = {statistics.median(rtts):.2f} ms, "
                        f"loss = {packet_loss:.1f}%"
                    )
                else:
                    print(
                        f"[{timestamp}] Series {series_number}: "
                        "no replies received"
                    )

                next_measurement += args.interval

    except KeyboardInterrupt:
        print("\nMeasurement stopped by user.")

    print(f"\nMeasurements saved to: {output_file}")


if __name__ == "__main__":
    main()

