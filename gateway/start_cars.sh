#!/bin/bash
# Start one controller page per car (after gateway.sh has brought the cars up):
#   gateway/start_cars.sh 4            -> pages on ports 8761..8764, open to the gateway's network
# Car N: http://<gateway address>:876N   (no password: use a network you trust)
# Stop with Ctrl-C. Needs ffmpeg on the gateway for phones whose browser can't decode H.264 directly
# (plain http:// pages from another machine are such a case).
set -e
n=${1:?usage: start_cars.sh <number of cars>}
here=$(cd "$(dirname "$0")" && pwd)
pids=()
trap 'kill "${pids[@]}" 2>/dev/null' EXIT INT TERM
for i in $(seq 1 "$n"); do
  python3 "$here/../termux/fpv_car.py" serve --car "$i" --listen 0.0.0.0 &
  pids+=($!)
  echo "car $i: port $((8760 + i))"
done
wait
