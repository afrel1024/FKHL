# FKHL

基于 Flask 的反向代理 Web 应用，支持 HTTPS、iframe 内嵌、SSL 证书和远程命令执行。

## 功能特性

- **反向代理** — 通过 `/proxy?url=目标URL` 转发 HTTP/HTTPS 请求，自动注入 JS 绕过 iframe 检测
- **iframe 内嵌页面** — 首页集成可输入 URL 加载的 iframe 和预置 Bing 代理 iframe
- **远程命令执行** — 通过 SSE（Server-Sent Events）流式执行系统命令并实时返回输出
- **Hosts 自动修改** — 启动时自动添加 `jzjx-prod-resource.hailiangedu.com` 的 hosts 映射
- **域名黑名单** — 内置域名过滤，拒绝访问黑名单中的域名
- **SSL/HTTPS 支持** — 自带自签名证书，提供 HTTPS 访问
- **自动提权** — 非管理员运行时自动请求管理员权限

## 快速开始

### 新电脑一键部署

将整个项目文件夹拷贝到目标电脑，双击运行：

```
setup.bat
```

脚本会自动完成以下步骤：
1. 检测系统中已有的 Python（3.x），若没有则自动下载 Python 嵌入版
2. 安装 pip
3. 安装项目依赖（Flask、flask-cors、requests、python-hosts）
4. 启动 Web 应用并自动打开浏览器访问 `https://127.0.0.1:5000`

### 已有环境快速启动

```
run.bat
```

### 手动启动

```powershell
# 测试模式（跳过管理员检查）
$env:FLASK_TEST_MODE="1"
$env:HOST_IP="127.0.0.1"
python app.py

# 生产模式（需管理员权限）
$env:HOST_IP="127.0.0.1"
python app.py
```

浏览器打开 `https://127.0.0.1:5000`，证书警告点击「高级 → 继续前往」。

## API 说明

| 路由 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 主页面 |
| `/proxy?url=<URL>` | GET | 代理转发到目标 URL，HTML 页面自动注入反检测脚本 |
| `/execute?command=<CMD>` | GET | 执行系统命令，SSE 流式返回结果 |
| `/sbhl` | GET | sbhl 页面 |

## 目录结构

```
prog/
├── app.py              # Flask 主应用
├── app.spec            # PyInstaller 打包配置
├── c.spec              # PyInstaller 打包配置（备用）
├── cert.pem            # SSL 证书
├── key.pem             # SSL 私钥
├── rootCA.pem          # CA 根证书
├── rootCA-key.pem      # CA 根证书私钥
├── requirements.txt    # Python 依赖清单
├── setup.bat           # 一键安装运行脚本
├── run.bat             # 快速启动脚本
├── flask.bat           # Flask 环境安装脚本
├── pack.bat            # PyInstaller 打包脚本
├── privacy.html        # 隐私页面
├── templates/
│   ├── index.html      # 主页面模板
│   ├── execute.html    # 命令执行页面
│   └── sbhl.html       # sbhl 页面
└── python/             # （自动生成）Python 嵌入版
```

## 依赖

- Python 3.8+
- Flask 3.x
- flask-cors
- requests
- python-hosts

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `HOST_IP` | hosts 映射的目标 IP | 必填 |
| `FLASK_TEST_MODE` | 设为 `1` 跳过管理员权限检查 | `0` |

## 打包为 exe

```bash
pack.bat
```

或手动：

```bash
pyinstaller --onefile --add-data "templates;templates" --hidden-import flask app.py
```

## Contributors

BlueGS · 绿云ps · Sonder · sukhoi · 金局长
