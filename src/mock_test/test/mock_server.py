# Initially from https://raw.githubusercontent.com/aio-libs/aiobotocore/master/tests/mock_server.py
import shutil
import signal
import subprocess as sp
import sys
import time

import requests


_proxy_bypass = {
    "http": None,
    "https": None,
}


def start_service(service_name, host, port):
    moto_svr_path = shutil.which("moto_server")
    args = [sys.executable, moto_svr_path, service_name, "-H", host, "-p", str(port)]
    process = sp.Popen(args, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.DEVNULL)
    url = "http://{host}:{port}".format(host=host, port=port)

    for _ in range(30):
        if process.poll() is not None:
            break

        try:
            # we need to bypass the proxies due to monkeypatches
            requests.get(url, timeout=0.1, proxies=_proxy_bypass)
            break
        except requests.exceptions.RequestException:
            time.sleep(0.1)
    else:
        stop_process(process)
        raise AssertionError("Can not start service: {}".format(service_name))

    return process


def stop_process(process, timeout=20):
    try:
        process.send_signal(signal.SIGTERM)
        process.communicate(timeout=timeout / 2)
    except sp.TimeoutExpired:
        process.kill()
        outs, errors = process.communicate(timeout=timeout / 2)
        exit_code = process.returncode
        msg = "Child process finished {} not in clean way: {} {}".format(
            exit_code, outs, errors
        )
        raise RuntimeError(msg)
