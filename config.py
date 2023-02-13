# encoding:utf-8

from common.log import logger
import os
import json
from pprint import pprint


config_path = os.path.dirname(os.path.abspath(__file__)) + '/config.json'


def read_config():
    if not os.path.exists(config_path):
        raise Exception('配置文件不存在，请根据config-template.json模板创建config.json文件')

    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        return None


def update_config():
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)


# fill configs
config = read_config()


def conf():
    return config


if __name__ == "__main__":
    pprint(config)
