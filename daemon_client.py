import json
import time

import requests
import yaml
from rich.console import Console
from rich.align import Align
from rich.table import Layout, Table
from rich.live import Live

console = Console()
layout = Layout()

connection_table = Table(show_header=True, header_style="bold magenta")
connection_table.add_column("Connection", style="dim", width=12)
connection_table.add_column("Status", justify="right")
connection_table = Align.center(connection_table)

process_table = Table(show_header=True, header_style="bold magenta")
process_table.add_column("Process", style="dim", width=12)
process_table.add_column("Status", justify="right")
process_table = Align.center(process_table)

rostopic_hz_table = Table(show_header=True, header_style="bold magenta")
rostopic_hz_table.add_column("Topic", style="dim", width=12)
rostopic_hz_table.add_column("Rate(hz)", justify="right")
rostopic_hz_table = Align.center(rostopic_hz_table)

# Divide the "screen" in to three parts
layout.split(
    Layout(connection_table),
    Layout(process_table),
    Layout(rostopic_hz_table),
)


with open("config.yml", "r") as f:
    config = yaml.safe_load(f)
    print(f"{config}")


if __name__ == "__main__":
    with Live(layout, screen=True):
        while True:
            try:
                url = f"http://{config['server_ip']}:{config['server_port']}"
                response = requests.get(url)
                status_dict = json.loads(response.content)

                # if code is 200, the connection is good, else the connection is bad
                if response.status_code == 200:
                    # print in "connection" part, name on the left and status on the right
                    connection_table.add_row(f"{config['server_ip']}:{config['server_port']}", "[green]OK")
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
            time.sleep(1)