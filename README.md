# nacos-client-py
监听nacos server配置中心，并拉取应用配置文件

# Usage
## 1.创建.env文件
**nacos服务器信息**
```shell
$ cat .env
nacos_server="192.168.1.1:8848"
nacos_namespace_id="fbea1ef7-2428-4516-9a38-487c99c7df7d"
nacos_suth_user="nacos"
nacos_auth_passwd="nacos"
```

## 2.创建配置文件信息
需要监听的配置文件
```shell
configs:
  - name: official-nginx
    id: official          # nacos data id
    group: haproxy          # nacos group
    path: "/etc/haproxy/haproxy.cfg"       # 服务器上配置文件路径
    command: "systemctl restart haproxy"      # 配置文件更新后，需要执行的命令
```

## 3.定制化脚本
```python
    # 回调函数，当监听到配置文件发生变化后，执行的操作
    def print_cm(self, status):
        snapshot_file = "{0}+{1}+{2}".format(status['data_id'], status['group'], NAMESPACE)
        for p in self.cf['configs']:
            if status['data_id'] == p['id'] and status['group'] == p['group']:
                shutil.copy("nacos-data/snapshot/{}".format(snapshot_file), p['path'])      # 将snapsho file复制到本地的文件路径
            s, r = subprocess.getstatusoutput(p['command'])
            if int(s) != 0:
                print("命令执行失败:{}".format(p['command']))
                return False
        return True
```

## 4.使用supervisor启动服务
启动命令
```shell
python3 nacos-get-config.py
```
