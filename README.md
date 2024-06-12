# browseMatu
（本文档由[Kimi](https://kimi.moonshot.cn)生成）

电子科技大学码图系统的自动化浏览和任务管理工具。

## 项目概述

本项目旨在自动化地浏览和下载电子科技大学码图系统中的任务和相关文件，同时记录任务的详细信息。

## 特性

- **自动化登录**：自动填写登录信息并登录码图系统。
- **链接收集**：自动收集码图系统中的任务链接。
- **表格解析**：从任务页面解析关键信息。
- **文件下载**：下载任务相关的代码文件。
- **任务记录**：将任务信息记录到本地文件中。

## 注意事项

- 代码注释部分由 GitHub Copilot 自动生成，可能需要人工复核以确保准确性。
- 存在缺陷：当前脚本未设置足够的等待时间，可能导致某些文件下载被跳过。

## 前提条件

- Python 3.10.6
- Selenium WebDriver
- 浏览器的 WebDriver（例如 ChromeDriver、EdgeDriver，本项目使用的是EdgeDriver，如使用其他WebDriver需相应调整initialize函数中webdriver的初始化部分）

## 安装

1. 克隆本仓库到本地机器：
```bash
git clone https://github.com/zahi-ko/browseMatu.git
```
2. 进入项目目录:
```bash
cd browseMatu
```
3. 安装必要的第三方库
```bash
pip install selenium==4.21.0
```
## 配置

在 `main.py` 文件中设置以下全局变量以匹配您的环境和需求：
- `DRIVER_PATH`：WebDriver 可执行文件的路径。
- `SAVE_PATH`：下载文件的保存路径。

在 `login`函数中设置你的码图用户名以及密码

## 使用方法

运行以下命令启动自动化脚本：
```bash
python main.py
```