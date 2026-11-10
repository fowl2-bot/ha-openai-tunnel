# HAOS systemd/cgroup feasibility probe

**Disposable test app, not for production.** Manual start only; no privileged capabilities, host mounts, Docker socket, Supervisor API access, or published ports. Debian + systemd are installed when the image is built.

## Install

1. In Home Assistant, open **Settings → Apps → Install app → ⋮ → Repositories** and add `https://github.com/fowl2-bot/ha-openai-tunnel` if not already installed.
2. Refresh repository updates from the app store menu.
3. Install **Systemd feasibility probe**. It builds its own amd64 image using the app Dockerfile. The first build downloads Debian packages.
4. Start it manually and inspect its **Logs** tab.
5. Stop/remove the test app after the experiment.

The probe logs its cgroup namespace, mount flags, controllers and capabilities; attempts to create a child cgroup; then execs systemd as PID 1. The systemd-managed unit reports `SYSTEMD_UNIT_STARTED` and `SYSTEMD_UNIT_COMPLETED` if it executes.

- `CREATE_CGROUP=failed: ... Read-only file system`: cgroup subtree was not delegated writable; systemd will likely fail.
- `Permission denied`: investigate namespaces, capabilities and security profiles.
- `CREATE_CGROUP=success` and unit markers: systemd successfully launched a managed unit. This doesn't establish all systemd features work.
- `CREATE_CGROUP=success` without unit markers: inspect subsequent systemd diagnostics.

The script makes no attempt to remount cgroups or modify the host. It uses Debian rather than NixOS to isolate the first question: whether HAOS container constraints permit running systemd.

**Security:** The app intentionally requests no extra capabilities or privileges. Do not grant host cgroup mounts or broad privileges just to make it start. If it fails, we can investigate what restricted cgroup delegation Supervisor would need.
