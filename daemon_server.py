import os
import threading
import uvicorn
import yaml
from fastapi import FastAPI
from func_timeout import func_set_timeout
from func_timeout.exceptions import FunctionTimedOut

app = FastAPI()

with open("config.yml", "r") as f:
    config = yaml.safe_load(f)
    print(f"{config}")


def check_process_exists(process_name):
    """
    Check if a process is running by name
    Args:
        process_name: str, name of the process

    Returns: bool, True if the process is running

    """
    # check using ps -ef | grep process_name
    output = os.popen(f"ps -ef | grep {process_name}").read()
    # format lines into a list
    lines = output.split("\n")
    # filter out empty lines
    lines = list(filter(lambda x: x != "", lines))
    # filter out grep process
    lines = list(filter(lambda x: "grep" not in x, lines))

    return len(lines) > 0

def get_ros_topic_hz(topic_name):
    """
    Get the hz of a ros topic via command line: rostopic hz topic_name
    Args:
        topic_name: str, name of the topic

    Returns: float, hz of the topic

    """

    @func_set_timeout(5)
    def _get_ros_topic_hz(topic_name):
        output = os.popen(f"python2 ./ros_hz.py {topic_name}").read()
        # format lines into a list
        lines = output.split("\n")
        # filter out empty lines
        lines = list(filter(lambda x: x != "", lines))
        # filter out grep process
        lines = list(filter(lambda x: "average rate" in x, lines))
        # get the hz
        if len(lines) == 0:
            return 0.0
        try:
            hz = float(lines[0].split(" ")[-1])
        except Exception as e:  # IndexError
            print(f"Error: _get_ros_topic_hz: {e}")
            hz = 0.0
        return hz

    try:
        return _get_ros_topic_hz(topic_name)
    except FunctionTimedOut:
        print(f"{topic_name} timed out")
        return 0.0


@app.get("/")
async def get_status():
    # check process
    process_checklist = config['process_checklist']
    process_status = {}

    # use a thread for each process to check process status
    threads = []
    for process_name in process_checklist:
        t = threading.Thread(target=lambda: process_status.update({process_name: check_process_exists(process_name)}))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    rostopic_hz_checklist = config['rostopic_hz_checklist']
    rostopic_hz = {}

    # check ros topic rate
    threads = []
    for topic_name in rostopic_hz_checklist:
        t = threading.Thread(target=lambda: rostopic_hz.update({topic_name: get_ros_topic_hz(topic_name)}))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    return {
        "process_status": process_status,
        "rostopic_hz": rostopic_hz
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config['server_port'])
