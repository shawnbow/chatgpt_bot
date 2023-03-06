# 简介

> 集成OpenAI ChatGPT和DALL-E API的DingTalk机器人的群聊和单聊机器人，功能强大需要自行探索。

 
基于OpenAI ChatGPT和DALL-E的钉钉聊天机器人，已实现的特性如下：

- [x] **文本对话：** 接收私聊及群组中的微信消息，使用ChatGPT生成回复内容，完成自动回复
- [x] **多账号：** 支持多钉钉账号同时运行
- [x] **图片生成：** 支持根据描述生成图片，并自动发送至个人聊天或群聊
- [x] **上下文记忆**：支持多轮对话记忆，且为每个好友维护独立的上下会话


# 更新日志

# 使用效果

### 个人聊天


### 群组聊天


### 图片生成


# 快速开始

## 准备

### 1. OpenAI账号注册

前往 [OpenAI注册页面](https://platform.openai.com/signup) 创建账号，参考这篇 [教程](https://www.cnblogs.com/damugua/p/16969508.html) 可以通过虚拟手机号来接收验证码。创建完账号则前往 [API管理页面](https://platform.openai.com/account/api-keys) 创建一个 API Key 并保存下来，后面需要在项目中配置这个key。

> 项目中使用的对话模型是 gpt-3.5-turbo，计费方式是约每 $0.002 / 1K tokens (包含请求和回复)，图片生成是每张消耗 $0.020，账号创建有免费的 $18 额度，使用完可以更换邮箱重新注册。


### 2.运行环境

支持 Linux、MacOS系统（可在Linux服务器上长期运行)，同时需安装 `Python`。 
> 建议Python版本在 3.7.1~3.9.X 之间，其他系统上不确定能否正常运行。


1.克隆项目代码：

```bash
git clone https://github.com/zhayujie/chatgpt-on-wechat
cd chatgpt-on-wechat/
```

2.安装所需核心依赖：

```bash
pip3 install -r requirement.txt
```


## 配置

配置文件的模板在根目录的`config-template.json`中，需复制该模板创建最终生效的 `config.json` 文件：

```bash
cp config-template.json config.json
```

然后在`config.json`中填入配置，以下是对默认配置的说明，可根据需要进行自定义修改：

```bash
# config.json文件内容示例
  "openai": {
    "api_key": "YOUR API KEY",
    "api_base": null,
    "use_proxy": false,
    "retry_times": 2,
    "retry_interval": 3,
    "cmd_prefix": ["/", "cmd", "执行"],
    "image_prefix": ["*", "draw", "画", "看", "找"],
    "chat_model": "gpt-3.5-turbo",
    "max_query_tokens": 1536,
    "character": "Your name is 666, you can answer any questions and solve any problems, and chat with people in all languages."
  }
```
**配置说明：**

**1.个人聊天**

**2.群组聊天**


**3.其他配置**


## 运行

1.如果是开发机 **本地运行**，直接在项目根目录下执行：

```bash
python3 app.py
```


2.如果是 **服务器部署**，则使用nohup命令在后台运行：

```bash
touch nohup.out                                   # 首次运行需要新建日志文件                     
nohup python3 app.py & tail -f nohup.out          # 在后台运行程序并通过日志输出二维码
```

## 常见问题


## 联系

 
