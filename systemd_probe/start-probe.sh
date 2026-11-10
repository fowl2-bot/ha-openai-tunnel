#!/bin/sh
# Reports container-local cgroup state; no host or Docker configuration changes.
set -u
echo '=== HAOS systemd/cgroup probe: before systemd ==='
echo "PID=$$; UID=$(id -u); kernel=$(uname -r)"
echo "cgroup filesystem: $(stat -f -c %T /sys/fs/cgroup 2>&1)"
echo 'cgroup mount:'
grep ' /sys/fs/cgroup ' /proc/self/mountinfo || true
echo 'process cgroup:'
cat /proc/self/cgroup || true
echo 'available cgroup controllers:'
cat /sys/fs/cgroup/cgroup.controllers 2>&1 || true
echo 'mount namespace:'
readlink /proc/self/ns/mnt || true
echo 'cgroup namespace:'
readlink /proc/self/ns/cgroup || true
echo 'capabilities:'
grep -E '^Cap(Eff|Bnd):' /proc/self/status || true
probe_path="/sys/fs/cgroup/haos-systemd-probe-$$"
if err=$(mkdir "$probe_path" 2>&1); then
    echo 'CREATE_CGROUP=success'
    rmdir "$probe_path" || true
else
    echo "CREATE_CGROUP=failed: $err"
fi
echo '=== Starting systemd as PID 1 ==='
exec /lib/systemd/systemd --log-target=console --log-level=info
