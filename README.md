# ros-daemon

守护进程服务器，用于获取机载电脑ros各节点运行状态。

## 运行

### Server端（飞机）

```bash
# 首先激活虚拟环境
# 然后：
python3 daemon_server.py
```

> [!NOTE]
> `ros_hz.py`由`daemon_server.py`通过命令行调用，需要使用系统Python环境（Python 2.7 对于ROS Melodic）运行。

### Client端

修改`config.yml`修改`server_ip`为Server端的IP地址，(不要含http://)。

```bash
# 首先激活虚拟环境
# 然后：
python3 client.py
```