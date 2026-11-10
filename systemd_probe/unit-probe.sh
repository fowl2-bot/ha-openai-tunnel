#!/bin/sh
set -eu
echo '=== SYSTEMD_UNIT_STARTED ==='
echo "PID=$$"
cat /proc/self/cgroup
echo '=== SYSTEMD_UNIT_COMPLETED ==='
