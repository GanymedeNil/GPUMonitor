import time
from nvitop import Device, GpuProcess
import os


def kill_process(pid):
    try:
        os.kill(pid, 9)
    except Exception:
        pass


INTERVAL = 5
THRESHOLD = 12

inactive_tracker = {}

while True:
    current_active_processes = set()
    devices = Device.cuda.all()
    for device in devices:
        processes = device.processes()
        if len(processes) > 0:
            processes = GpuProcess.take_snapshots(processes.values(), failsafe=True)
            processes.sort(key=lambda p: (p.username, p.pid))
            for snapshot in processes:
                key = (device.index, snapshot.pid)
                current_active_processes.add(key)

                # Update tracker for active processes
                if snapshot.gpu_sm_utilization == 0 and snapshot.cpu_percent <= 1.0:
                    inactive_tracker[key] = inactive_tracker.get(key,0) + 1
                else:
                    inactive_tracker[key] = 0

                # Kill process if it meets the criteria
                if inactive_tracker[key] >= THRESHOLD:
                    kill_process(snapshot.pid)
                    inactive_tracker.pop(key, None)

    # Clean up tracker for any process not active anymore
    inactive_tracker = {key: count for key, count in inactive_tracker.items() if key in current_active_processes}

    time.sleep(INTERVAL)