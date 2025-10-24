#!/bin/bash

# Usage: ./run_server.sh <host> <port>

HOST=$1
PORT=$2

dname=$(dirname ${BASH_SOURCE[0]})


if [ -z "$HOST" ] || [ -z "$PORT" ]; then
  echo "Usage: $0 <host> <port>"
  exit 1
fi

python3 "$dname/part2.py" "$HOST" "$PORT"