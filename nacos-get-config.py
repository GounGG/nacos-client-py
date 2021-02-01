#!/usr/bin/env python3
# coding:utf-8

import os
import shutil
import subprocess
from datetime import datetime

import nacos
import yaml
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv, find_dotenv

# load .env file
load_dotenv(find_dotenv(), override=True)

SERVER_ADDRESSES = os.getenv("nacos_server")
NAMESPACE = os.getenv("nacos_namespace_id")
USERNAME = os.getenv("nacos_suth_user")
PASSWORD = os.getenv("nacos_auth_passwd")

# auth mode
client = nacos.NacosClient(SERVER_ADDRESSES, namespace=NAMESPACE, username=USERNAME, password=PASSWORD)
client.set_options(callback_thread_num=1)


class Watcher():
    def __init__(self):
        self.cf = cf

    def run(self):
        for p in self.cf['configs']:
            self.cf_path = p['path']
            self.watch(id=p['id'], group=p['group'])

    def print_cm(self, status):
        snapshot_file = "{0}+{1}+{2}".format(status['data_id'], status['group'], NAMESPACE)
        for p in self.cf['configs']:
            if status['data_id'] == p['id'] and status['group'] == p['group']:
                shutil.copyfileobj(open("nacos-data/snapshot/{}".format(snapshot_file), "rb"), open(p['path'], "wb"))
            s, r = subprocess.getstatusoutput(p['command'])
            if int(s) != 0:
                print("命令执行失败:{}".format(p['command']))
                return False
        return True

    def watch(self, id, group):
        client.add_config_watcher(id, group, self.print_cm)


if __name__ == '__main__':
    # 传入配置
    with open('config.yaml', 'r+') as f:
        cf = yaml.load(f)

    # # 常驻调度任务
    scheduler = BlockingScheduler()
    job = Watcher()
    # 每隔1分钟执行一次 job_func;
    scheduler.add_job(job.run, 'interval', minutes=1)
    try:
        print("{0} nacos watch the process start".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("{0} nacos watch the process exit".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        scheduler.shutdown()
