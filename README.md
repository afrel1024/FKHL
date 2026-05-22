# FKHL

基于 Flask 的反向代理 Web 应用，支持 HTTPS、iframe 内嵌、SSL 证书和远程命令执行。

***

## 功能特性

- **反向代理** — 通过 `/proxy?url=目标URL` 转发 HTTP/HTTPS 请求，自动注入 JS 绕过 iframe 检测
- **iframe 内嵌页面** — 首页集成可输入 URL 加载的 iframe 和预置 Bing 代理 iframe
- **远程命令执行** — 通过 SSE（Server-Sent Events）流式执行系统命令并实时返回输出
- **Hosts 自动修改** — 启动时自动添加 `jzjx-prod-resource.hailiangedu.com` 的 hosts 映射
- **域名黑名单** — 内置域名过滤，拒绝访问黑名单中的域名
- **SSL/HTTPS 支持** — 自带自签名证书，提供 HTTPS 访问
- **自动提权** — 非管理员运行时自动请求管理员权限

## 已测试可用网站

- **网易云游戏 [cg.163.com](http://cg.163.com)** — 可用**
- **百度搜索** **[www.baidu.com](http://www.baidu.com)** **— 可用**
- **咪咕快游 [www.migufun.com](http://www.migufun.com)** — 可用**
- **必应** **[www.bing.com](http://www.bing.com)** **—** ***不可用***

***

## 快速开始

### 📦 使用安装包（推荐）

只需三步即可完成部署：

1. **下载安装包**\
   获取 `FKHL-Setup.exe`
2. **运行安装程序**\
   双击 `FKHL-Setup.exe`，安装程序会自动：
   - 检测 Python 环境
   - 若未安装 Python，弹出提示并提供下载链接
   - 在线安装项目依赖
   - 创建桌面快捷方式
3. **启动应用**\
   双击桌面快捷方式即可启动

### 🖥️ 手动部署

**新电脑一键部署：**

```bash
setup.bat
```

**已有环境快速启动：**

```bash
run.bat
```

**手动启动：**

```powershell
# 设置环境变量
$env:HOST_IP="192.168.137.1"

# 生产模式（需管理员权限）
python app.py
```

访问地址：`https://jzjx-prod-resource.hailiangedu.com`\
首次访问会有证书警告，点击「高级 → 继续前往」即可。

***

## API 接口

| 路由                       | HTTP 方法 | 说明               |
| ------------------------ | ------- | ---------------- |
| `/`                      | GET     | 主页面              |
| `/proxy?url=<URL>`       | GET     | 代理转发到目标 URL      |
| `/execute?command=<CMD>` | GET     | 执行系统命令（SSE 流式返回） |
| `/sbhl`                  | GET     | SBHL 页面          |

### 示例

**代理访问网站：**

```
https://192.168.137.1:443/proxy?url=https://www.example.com
```

**执行系统命令：**

```
https://192.168.137.1:443/execute?command=ls
```

***

## 配置说明

### 环境变量

| 变量名               | 说明               | 默认值           |
| ----------------- | ---------------- | ------------- |
| `HOST_IP`         | hosts 映射的目标 IP   | 192.168.137.1 |
| `FLASK_TEST_MODE` | 设为 `1` 跳过管理员权限检查 | `0`           |

### 项目结构

```
FKHL/
├── app.py              # Flask 主应用
├── requirements.txt    # Python 依赖清单
├── LICENSE             # GNU General Public License v3.0 - 许可证
├── cert.pem            # SSL 证书
├── key.pem             # SSL 私钥
├── rootCA.pem          # 根 CA 证书，用于验证 SSL 证书的签名
├── rootCA-key.pem      # 根 CA 私钥，用于生成 SSL 证书
├── templates/          # HTML 模板
   ├── index.html      # 主页面
   ├── execute.html    # 命令执行页面
   └── sbhl.html       # SBHL 页面

```

***

## 开发指南

### 依赖要求

- Python 3.8+
- Flask 3.x
- flask-cors
- requests
- python-hosts

### 安装依赖

```bash
pip install -r requirements.txt
```

### 开发模式

```powershell
$env:FLASK_TEST_MODE="1"
$env:HOST_IP="192.168.137.1"
python app.py
```

***

## 安装包功能

`FKHL-Setup.exe` 具备以下特性：

- ✅ 自动检测 Python 环境
- ✅ Python 未安装时弹窗提示并提供下载链接
- ✅ 自动在线安装项目依赖
- ✅ 创建桌面和开始菜单快捷方式
- ✅ 支持标准卸载流程

***

## 许可证

MIT License - 详见 [LICENSE.txt](LICENSE.txt)

***

## 贡献者

BlueGS · 绿云ps · Sonder · sukhoi · 金局长
