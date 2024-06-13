import time

import torch.multiprocessing as mp
import torch
def worker(is_loading: bool = False):
    x = torch.rand(1000, 30)
    x.to("cuda:0")
    y = torch.rand(30, 1000)
    y.to("cuda:0")
    if is_loading:
        while True:
            x @ y
            time.sleep(1)
    time.sleep(1000)
def main():
    mp.set_start_method('spawn', force=True)

    x = torch.rand(10, 3)
    x.to("cuda:0")

    n_workers = 4
    processes = []

    for rank in range(n_workers):
        p = mp.Process(target=worker, args=(True,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()


if __name__ == "__main__":
    main()