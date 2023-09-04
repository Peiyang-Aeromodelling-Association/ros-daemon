# ros-daemon

守护进程服务器，用于获取机载电脑ros各节点运行状态。

## 运行

### Server端（飞机）

```bash
# 首先激活虚拟环境
# 然后：
python3 daemon_server.py
```

### Client端

修改`config.yml`修改`server_ip`为Server端的IP地址，(不要含http://)。

```bash
# 首先激活虚拟环境
# 然后：
python3 client.py
```