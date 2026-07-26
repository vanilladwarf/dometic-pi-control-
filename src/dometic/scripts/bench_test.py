#!/usr/bin/env python3
"""Bench-test the relay HAT without mains. Cycles each relay on/off."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import RPi.GPIO as GPIO


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    pins = [17, 27, 22, 23, 24, 5, 13, 19]
    for p in pins:
        GPIO.setup(p, GPIO.OUT, initial=GPIO.HIGH)
    try:
        print("Press Ctrl-C to abort.")
        while True:
            for p in pins:
                print(f"  -> GPIO {p:>2} ON")
                GPIO.output(p, GPIO.LOW)
                time.sleep(1.0)
                GPIO.output(p, GPIO.HIGH)
                time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        for p in pins:
            GPIO.output(p, GPIO.HIGH)
        print("\nDone.")


if __name__ == "__main__":
    main()
