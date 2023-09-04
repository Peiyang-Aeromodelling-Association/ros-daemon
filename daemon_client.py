import json
import time

import requests
import yaml
from rich.console import Console
from rich.table import Table

console = Console()

with open("config.yml", "r") as f:
    config = yaml.safe_load(f)
    print(f"{config}")

if __name__ == "__main__":
    while True:
        try:
            url = f"http://{config['server_ip']}:{config['server_port']}"
            response = requests.get(url)
            status_dict = json.loads(response.content)

            # if code is 200, the connection is good, else the connection is bad
            if response.status_code == 200:
                connection_table = Table(show_header=True, header_style="bold magenta")
                connection_table.add_column("Connection", style="dim", width=12)
                connection_table.add_column("Status", justify="right")
                connection_table.add_row(f"{config['server_ip']}:{config['server_port']}", "[green]OK")
                console.print(connection_table)
            else:
                raise Exception(f"Connection Error: {response.status_code}")

            # display process_checklist to check process is running. if True, display green [OK], else display
            # red [ERROR]  all these are displayed with process name on the left and status on the right
            process_table = Table(show_header=True, header_style="bold magenta")
            process_table.add_column("Process", style="dim", width=12)
            process_table.add_column("Status", justify="right")
            for process_name, process_status in status_dict["process_status"].items():
                if process_status:
                    process_table.add_row(process_name, "[green]OK")
                else:
                    process_table.add_row(process_name, "[red]ERROR")
            console.print(process_table)

            # display rostopic_hz_checklist to check the rate of rostopic, the name of the rostopic is on the left and the rate is on the right
            rostopic_hz_table = Table(show_header=True, header_style="bold magenta")
            rostopic_hz_table.add_column("Topic", style="dim", width=12)
            rostopic_hz_table.add_column("Rate(hz)", justify="right")
            for topic_name, topic_hz in status_dict["rostopic_hz"].items():
                rostopic_hz_table.add_row(topic_name, f"{topic_hz:.2f}")
            console.print(rostopic_hz_table)
        except Exception as e:
            connection_table = Table(show_header=True, header_style="bold magenta")
            connection_table.add_column("Connection", style="dim", width=12)
            connection_table.add_column("Status", justify="right")
            connection_table.add_row(f"{config['server_ip']}:{config['server_port']}", "[red]ERROR")
            console.print(connection_table)
            print(f"Error: {e}")
        time.sleep(1)
