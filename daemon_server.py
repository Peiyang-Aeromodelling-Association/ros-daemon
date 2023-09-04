import os

import uvicorn
import yaml
from fastapi import FastAPI

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
    output = os.popen(f"python ./ros_hz.py {topic_name}").read()
    # format lines into a list
    lines = output.split("\n")
    # filter out empty lines
    lines = list(filter(lambda x: x != "", lines))
    # filter out grep process
    lines = list(filter(lambda x: "average rate" in x, lines))
    # get the hz
    try:
        hz = float(lines[0].split(" ")[0])
    except Exception as e:  # IndexError
        print(f"Error: {e}")
        hz = 0.0
    return hz


@app.get("/")
async def get_status():
    # check process
    process_checklist = config['process_checklist']
    process_status = {}
    for process_name in process_checklist:
        process_status[process_name] = check_process_exists(process_name)

    # check ros topic rate
    rostopic_hz_checklist = config['rostopic_hz_checklist']
    rostopic_hz = {}
    for topic_name in rostopic_hz_checklist:
        rostopic_hz[topic_name] = get_ros_topic_hz(topic_name)

    return {
        "process_status": process_status,
        "rostopic_hz": rostopic_hz
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config['server_port'])
