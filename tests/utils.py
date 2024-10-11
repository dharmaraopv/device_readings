from threading import Thread


def worker(fn, args, result, index):
    result[index] = fn(*args)


def run_multiples_threads(fn, args):
    result = [None] * len(args)
    threads = [Thread(target=worker, args=[fn, arg, result, i]) for i, arg in enumerate(args)]
    for i in range(len(threads)):
        threads[i].start()

    for i in range(len(threads)):
        threads[i].join()
    return result
