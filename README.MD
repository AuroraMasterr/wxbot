# wxbot

一个基于 `wxauto` 的微信自动化机器人项目，支持：
- 监听指定会话并自动回复
- 指令触发（如 `/summary`）
- 定时任务（整点/间隔）
- 联动 `Trade` 项目：定时生成K线图并发送给指定联系人

## 环境要求

- Windows 10/11
- 微信桌面版（当前代码基于 3.9.12 生态）
- Python 3.9

## 项目结构

- `demo.py`：消息监听主入口（自动回复）
- `chatgpt.py`：LLM 对话封装
- `instruction.py`：指令路由与处理
- `utils.py`：消息过滤与清洗
- `monitor.py`：定时调度与图表推送（可联动 Trade）
- `wxauto/`：本地微信自动化能力

## 快速开始

1. 安装依赖（按你本地环境安装 `wxauto` 相关依赖）
2. 配置环境变量（用于 `chatgpt.py`）

```powershell
$env:OPENAI_API_KEY="你的key"
$env:OPENAI_URL="你的base_url"
```

3. 运行消息监听

```powershell
python demo.py
```

## 定时任务（monitor）

`monitor.py` 提供两种能力：

- 固定间隔执行：`run_interval(...)`
- 业务任务函数：`send_hourly_trade_chart(...)`

当前默认任务逻辑：
- 每到整点拉取 `Trade` 图表
- 若最后1小时K线振幅 `> 0.5%`，则发送：
  - 一条摘要文字（振幅、涨跌幅、收盘价）
  - 一张K线拼图

你可以直接运行：

```powershell
python monitor.py
```

## 与 Trade 项目联动

`monitor.py` 会动态引入同级目录下的 `Trade`：
- 调用 `draw.candlestick_drawer` 生成多周期图
- 使用 `wx.SendFiles(...)` 发送图片
- 使用 `wx.SendMsg(...)` 发送文字摘要

请确保目录结构为：

```text
repos/
  wxbot/
  Trade/
```

## 注意事项

- 本项目依赖桌面微信UI自动化，运行时请保持微信已登录且窗口可操作。
- 机器人发送对象（如 `fzx`）需与你微信会话名称一致。
- 生产使用建议增加异常告警、重试和日志落盘。
