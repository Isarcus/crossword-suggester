import platform
import atexit
from typing import Union
from subprocess import Popen, PIPE
from threading import Thread, Lock
from pathlib import Path
from queue import Queue, Empty
from time import sleep

_request = None
_thread = None
_run = False
_result = None
_shutdown_registered = False

_STR_DONE_SUGGESTING = "---"
_STR_IGNORE_LINE = "#"
_CMD_QUIT = "\n!Q\n"

_mutex = Lock()

def init():
    """
    Initialize the word suggester. This must only be called once, unless
    `shutdown()` has been called since the last `init()` call. Otherwise
    raises RuntimeError.
    """
    global _thread, _run, _shutdown_registered
    if _run:
        raise RuntimeError("init called twice before suggester allowed to terminate")
    else:
        if not _shutdown_registered:
            atexit.register(shutdown)
            _shutdown_registered = True
        _run = True
        _thread = Thread(target=_suggester_main)
        _thread.setDaemon(True)
        _thread.start()

def send_request(request: str):
    """
    Send a request to the suggester program.
    Results can be obtained by calling `get_result()`.
    """
    global _request
    with _mutex:
        _request = request

def get_result() -> Union[list[str], None]:
    """
    Returns the result of the last `send_request()` call, if available.
    Also erases the current result list upon a successful call, so the results
    of an individual call to `send_request()` can only be obtained once.
    If no results are available, returns None.
    """
    global _result
    result = None
    with _mutex:
        if _result is not None:
            result = _result
            _result = None
    return result

def shutdown():
    """
    Nicely shuts down the threads operating the suggester program.
    This function is automatically scheduled to run at exit upon `init()`
    being called for the first time, but it's still a good idea to call this
    at the end of your program.
    """
    global _run, _thread
    with _mutex:
        _run = False
    
    if _thread is not None:
        _thread.join(0.5)
        _thread = None

def _suggester_main():
    """Do not call this function directly. Call init() instead."""

    global _request, _run, _result

    # Start the subprocess
    exe_name = "suggester"
    if platform.system() == "Windows":
        exe_name += ".exe"
    root_dir = Path(__file__).parent.parent
    exe_path = root_dir.joinpath(exe_name)
    dict_path = root_dir.joinpath("data").joinpath("american.txt")
    proc = Popen([str(exe_path), str(dict_path)], stdout=PIPE, stderr=PIPE, stdin=PIPE)
    
    # Start thread for reading subprocess output
    q_stdout = Queue()
    thread_read = Thread(target=_queue_output, args=(proc.stdout, q_stdout))
    thread_read.setDaemon(True)
    thread_read.start()

    result = []
    reading = False
    request = None
    run = True
    try:
        while run:
            with _mutex:
                run = _run
                if not reading:
                    request = _request
                    _request = None

            if reading:
                try:
                    line = q_stdout.get_nowait().decode("utf-8").strip()
                except Empty:
                    pass
                except UnicodeDecodeError:
                    print("[suggester] Could not decode subprocess output")
                else:
                    # Ignore lines used as prompts
                    if line.startswith(_STR_IGNORE_LINE):
                        pass
                    # If final suggestion reached, finish reading and output result
                    elif line.startswith(_STR_DONE_SUGGESTING):
                        reading = False
                        with _mutex:
                            _result = result
                        result = []
                    # If just another suggestion, append to result
                    else:
                        result.append(line)
            elif request is not None:
                # Send request to stdin
                request += '\n'
                proc.stdin.write(request.encode("utf-8"))
                proc.stdin.flush()
                reading = True
            else:
                sleep(0.05)
    finally:
        proc.stdin.write(_CMD_QUIT.encode("utf-8"))
        proc.kill()
        print("Suggester thread terminating.")

def _queue_output(out, queue):
    """
    Super handy function for reading lines from a subprocess without blocking:
    https://stackoverflow.com/questions/375427/a-non-blocking-read-on-a-subprocess-pipe-in-python
    """
    try:
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()
    finally:
        print("Queue output thread terminating.")
