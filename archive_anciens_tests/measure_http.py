
import argparse
import csv
import time
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError, HTTPError


# Project directories
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "raw"
URL = "https://open.spotify.com/"


def measure_http():
    start = time.perf_counter()
    status = ""
    error = ""

    try:
        with urlopen(URL, timeout=15) as response:
            status = response.status
            response.read(1024)

    except HTTPError as exc:
        status = exc.code
        error = f"HTTP {exc.code}: {exc.reason}"

    except (URLError, TimeoutError, OSError) as exc:
        error = str(exc)

    total_time = time.perf_counter() - start

    return total_time, status, error


def main():
    parser = argparse.ArgumentParser(
        description="Measure HTTPS access time to Spotify."
    )
    parser.add_argument("--duration", type=int, default=3600,
                        help="Measurement duration in seconds")
    parser.add_argument("--interval", type=int, default=900,
                        help="Time between measurements in seconds")
    parser.add_argument("--location", default="home")
    parser.add_argument("--network", default="wifi")
    args = parser.parse_args()

    if args.duration < 1 or args.interval < 1:
        parser.error("Duration and interval must be positive.")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = DATA_DIR / f"http_{session_id}.csv"

    columns = [
        "session_id", "timestamp", "target", "url",
        "location", "network", "total_time_s",
        "http_status", "error"
    ]

    start_time = time.monotonic()
    next_measurement = start_time

    print(f"Target: {URL}")
    print(f"Duration: {args.duration}s")
    print(f"Interval: {args.interval}s")
    print(f"Results: {output_file}")
    print("Press Ctrl+C to stop early.\n")

    try:
        with output_file.open(
            "w", newline="", encoding="utf-8"
        ) as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=columns
            )
            writer.writeheader()
            csvfile.flush()

            while time.monotonic() - start_time < args.duration:
                delay = next_measurement - time.monotonic()
                if delay > 0:
                    time.sleep(delay)

                if time.monotonic() - start_time >= args.duration:
                    break

                timestamp = datetime.now().astimezone().isoformat(
                    timespec="seconds"
                )

                total, status, error = measure_http()

                writer.writerow({
                    "session_id": session_id,
                    "timestamp": timestamp,
                    "target": "Spotify",
                    "url": URL,
                    "location": args.location,
                    "network": args.network,
                    "total_time_s": round(total, 4),
                    "http_status": status,
                    "error": error,
                })
                csvfile.flush()

                print(
                    f"[{timestamp}] HTTP={status or 'ERROR'} "
                    f"Total={total:.3f}s "
                    f"{error}"
                )

                next_measurement += args.interval

    except KeyboardInterrupt:
        print("\nMeasurement stopped by user.")

    print(f"\nMeasurements saved to: {output_file}")


if __name__ == "__main__":
    main()

