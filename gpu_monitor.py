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

            gpu_process_tree = {}
            pid_to_snapshot = {snapshot.pid: snapshot for snapshot in processes}
            for snapshot in processes:
                if snapshot.ppid in gpu_process_tree:
                    gpu_process_tree[snapshot.ppid].append(snapshot.pid)
                else:
                    gpu_process_tree[snapshot.pid] = [snapshot.pid]

            for ppid, pids in gpu_process_tree.items():
                key = (device.index, ppid)
                current_active_processes.add(key)
                for pid in pids:
                    if pid_to_snapshot[pid].gpu_sm_utilization == 0 and pid_to_snapshot[pid].cpu_percent <= 1.0:
                        inactive_tracker[key] = inactive_tracker.get(key, 0) + 1
                    else:
                        inactive_tracker[key] = 0
                if inactive_tracker[key] >= THRESHOLD:
                    kill_process(ppid)
                    inactive_tracker.pop(key, None)

    # Clean up tracker for any process not active anymore
    inactive_tracker = {key: count for key, count in inactive_tracker.items() if key in current_active_processes}

    time.sleep(INTERVAL)