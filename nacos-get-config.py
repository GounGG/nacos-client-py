#!/usr/bin/env python3
# coding:utf-8

import argparse
import os, json
import yaml
import shutil
import subprocess

import nacos
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


class Watcher():
    def __init__(self):
        self.cf = cf

    def run(self):
        for p in self.cf['configs']:
            self.cf_path = p['path']
            self.watch(name=p['name'], id=p['id'], group=p['group'])

    def print_cm(self, status):
        snapshot_file = "{0}+{1}+{2}".format(status['data_id'], status['group'], NAMESPACE)
        for p in self.cf['configs']:
            if status['data_id'] == p['id'] and status['group'] == p['group']:
                shutil.copy("/Users/jipu.fang/PycharmProjects/Jl/nacos-data/snapshot/{}".format(snapshot_file), p['path'])
            s, r = subprocess.getstatusoutput(p['command'])
            if int(s) != 0:
                print("命令执行失败:{}".format(p['command']))
                return False
        return True

    def watch(self, name, id, group):
        client.add_config_watcher(id, group, self.print_cm, content=name)


if __name__ == '__main__':
    # 传入配置
    with open('/Users/jipu.fang/PycharmProjects/Jl/nacos-tools/config.yaml', 'r+') as f:
        cf = yaml.load(f, Loader=yaml.FullLoader)

    # # 常驻调度任务
    scheduler = BlockingScheduler()
    job = Watcher()
    # 每隔1分钟执行一次 job_func;
    scheduler.add_job(job.run, 'interval', minutes=1)
    scheduler.start()