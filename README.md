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

### 使用安装包（推荐）

1. 下载 `FKHL-Setup.exe`
2. 双击运行安装程序
3. 安装程序会自动检测 Python 环境并安装依赖
4. 安装完成后自动创建桌面快捷方式

### 手动部署

**新电脑一键部署：**
```
setup.bat
```

**已有环境快速启动：**
```
run.bat
```

**手动启动：**
```powershell
# 设置环境变量
$env:HOST_IP="127.0.0.1"

# 测试模式（跳过管理员检查）
$env:FLASK_TEST_MODE="1"
python app.py

# 生产模式（需管理员权限）
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

## 项目结构

```
FKHL/
├── app.py              # Flask 主应用
├── app.spec            # PyInstaller 打包配置
├── requirements.txt    # Python 依赖清单
├── build.ps1           # 安装包构建脚本
├── installer.nsi       # NSIS 安装脚本
├── LICENSE.txt        # 许可证
├── templates/
│   ├── index.html     # 主页面模板
│   ├── execute.html   # 命令执行页面
│   └── sbhl.html      # sbhl 页面
└── dist/              # 打包输出目录
    ├── FKHL-Setup.exe  # 安装包
    ├── FKHL.exe       # 主程序
    ├── app.py         # 源码
    └── templates/     # 模板目录
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

## 构建安装包

使用 `build.ps1` 脚本自动完成所有打包步骤：

```powershell
.\build.ps1
```

脚本会自动：
1. 运行 PyInstaller 打包主程序
2. 复制项目文件到 dist 目录
3. 检测并安装 NSIS（如果未安装）
4. 生成 `FKHL-Setup.exe` 安装包

## 安装程序功能

`FKHL-Setup.exe` 安装包提供以下功能：
- 自动检测 Python 环境
- Python 未安装时弹出提示并提供下载链接
- 自动安装项目依赖
- 创建桌面和开始菜单快捷方式
- 支持卸载

## Contributors

BlueGS · 绿云ps · Sonder · sukhoi · 金局长
