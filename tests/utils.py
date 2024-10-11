from threading import Thread


def worker(fn, args, result, index):
    """
    Worker function to execute a given function with arguments and store the result.

    This function is designed to be run in a separate thread. It calls the specified function
    `fn` with the provided arguments `args`, and stores the result in the `result` list at the
    given `index`.

    Args:
        fn (Callable): The function to be executed.
        args (tuple): The arguments to pass to the function.
        result (list): A shared list to store the result of the function execution.
        index (int): The index in the result list where the function's result should be stored.
    """
    result[index] = fn(*args)  # Execute function with arguments and store result


def run_multiples_threads(fn, args):
    """
    Run multiple threads to execute a function with different arguments concurrently.

    This function initializes and starts a separate thread for each set of arguments in `args`.
    Each thread runs the `worker` function, which executes `fn` with the given arguments and stores
    the result in a shared list. Once all threads have completed execution, it returns the list
    containing the results from all threads.

    Args:
        fn (Callable): The function to be executed by each thread.
        args (list of tuples): A list where each element is a tuple of arguments for `fn`.

    Returns:
        list: A list containing the results from each thread's execution of `fn`.
    """
    # Initialize a result list with None values to store outputs from each thread
    result = [None] * len(args)

    # Create threads to execute the worker function with the respective arguments
    threads = [Thread(target=worker, args=[fn, arg, result, i]) for i, arg in enumerate(args)]

    # Start all threads
    for i in range(len(threads)):
        threads[i].start()

    # Wait for all threads to complete
    for i in range(len(threads)):
        threads[i].join()

    # Return the collected results from all threads
    return result
