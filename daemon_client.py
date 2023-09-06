import json
import time
import os
import requests
import yaml
from func_timeout import func_set_timeout
from func_timeout.exceptions import FunctionTimedOut
from rich.align import Align
from rich.console import Console
from rich.table import Table

console = Console()
with open("config.yml", "r") as f:
    config = yaml.safe_load(f)
    print(f"{config}")


def ping(ip):
    """
    Ping the server
    Args:
        ip: the ip of the server

    Returns: bool, True if ping success

    """
    @func_set_timeout(5)
    def _ping(ip):
        output = os.popen(f"ping {ip} -c 1")

        if "1 received" in output.read():
            return True
        else:
            return False

    try:
        return _ping(ip)
    except FunctionTimedOut:
        return False


if __name__ == "__main__":
    request_cnt = 0
    while True:
        request_cnt += 1
        console.print(f"request_cnt: {request_cnt}", end="\r")

        connection_table = Table(show_header=True, header_style="bold magenta")
        connection_table.add_column("Connection", style="dim", width=60)
        connection_table.add_column("Status", justify="right", width=5)

        process_table = Table(show_header=True, header_style="bold magenta")
        process_table.add_column("Process", style="dim", width=60)
        process_table.add_column("Status", justify="right", width=5)

        rostopic_hz_table = Table(show_header=True, header_style="bold magenta")
        rostopic_hz_table.add_column("Topic", style="dim", width=60)
        rostopic_hz_table.add_column("Rate(hz)", justify="right", width=5)

        try:
            ping_status = ping(config['server_ip'])
            if ping_status:
                connection_table.add_row(f"Ping: {config['server_ip']}", "[green]OK")
            else:
                connection_table.add_row(f"Ping: {config['server_ip']}", "[red]ERROR")

            url = f"http://{config['server_ip']}:{config['server_port']}"
            response = requests.get(url)
            status_dict = json.loads(response.content)

            # if code is 200, the connection is good, else the connection is bad
            if response.status_code == 200:
                # print in "connection" part, name on the left and status on the right
                connection_table.add_row(f"GET: {config['server_ip']}:{config['server_port']}", "[green]OK")
            else:
                raise Exception(f"Connection Error: {response.status_code}")

            # print in "process" part, name on the left and status on the right
            for process_name, process_status in status_dict["process_status"].items():
                if process_status:
                    process_table.add_row(process_name, "[green]OK")
                else:
                    process_table.add_row(process_name, "[red]ERROR")

            # print in "rostopic" part, name on the left and status on the right
            for topic_name, topic_hz in status_dict["rostopic_hz"].items():
                rostopic_hz_table.add_row(topic_name, f"{topic_hz:.2f}")
        except Exception as e:
            connection_table.add_row(f"{config['server_ip']}:{config['server_port']}", "[red]ERROR")
            print(f"Error: {e}")

        # clear the console
        console.clear()
        # display the table
        console.print(Align.center(connection_table, vertical="middle"))
        console.print(Align.center(process_table, vertical="middle"))
        console.print(Align.center(rostopic_hz_table, vertical="middle"))
        time.sleep(1)
