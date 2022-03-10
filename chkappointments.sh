#!/usr/bin/env bash
cd "$(dirname "$0")"
source ./pushover.env && poetry run python3 ./check_appointments.py


