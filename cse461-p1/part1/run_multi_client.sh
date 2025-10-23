#!/bin/bash

# Usage: ./run_client.sh <host> <port>

HOST=$1
PORT=$2

dname=$(dirname ${BASH_SOURCE[0]})


if [ -z "$HOST" ] || [ -z "$PORT" ]; then
  echo "Usage: $0 <host> <port>"
  exit 1
fi

for i in {1..4}; do
  echo "Starting process $i..."
  python "$dname/part1.py" "$HOST" "$PORT" &
done

wait

