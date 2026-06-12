from concurrent.futures import thread
import subprocess
from tokenize import Comment
from flask import Flask, Response, render_template,request,make_response,jsonify, send_from_directory
import os
from flask_cors import CORS
import time
import requests
from urllib.parse import urlparse,urljoin
import sys
import ctypes
from python_hosts import Hosts,HostsEntry
ip=os.getenv("HOST_IP","192.168.137.1")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

try:
    hosts=Hosts(path=r'C:\Windows\System32\drivers\etc\hosts')
    hosts.remove_all_matching(name='jzjx-prod-resource.hailiangedu.com')
    new_entry=HostsEntry(entry_type='ipv4',address=ip,names=['jzjx-prod-resource.hailiangedu.com'])
    hosts.add([new_entry])
except Exception as e:
    print(f"Warning: hosts modification skipped - {e}")

app = Flask(__name__)
CORS(app,resources={r"/":{"origins":""}})
# 设置用于加密session的密钥
app.secret_key = os.getenv("SECRET_KEY", "secret-key-example-default")

# 配置默认的用户名和密码（可通过环境变量修改）
AUTH_USERNAME = os.getenv("AUTH_USERNAME", "admin")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "admin")

# Session存储已登录状态
@app.route('/login', methods=['POST'])
def login():
    """登录验证"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username == AUTH_USERNAME and password == AUTH_PASSWORD:
        # 登录成功，设置session
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "账号或密码错误"}), 401

@app.route('/auth-status')
def auth_status():
    """检查是否已登录"""
    # 这里我们使用简单的验证方式，后续可扩展为session验证
    return jsonify({"authenticated": True})  # TODO: 实现真实的session验证

# 验证装饰器函数
def check_auth(username, password):
    return username == AUTH_USERNAME and password == AUTH_PASSWORD

DENIED_DOMAINS={"example.com"}#域名黑名单
def is_safe_url(target_url):
    parsed=urlparse(target_url)
    return parsed.netloc not in DENIED_DOMAINS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/proxy')
def proxy():
    """
    代理路由：转发请求到目标URL并处理响应
    注入JavaScript代码以修改window对象属性
    """
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({"error": "Missing 'url' parameter"}), 400
    if not is_safe_url(target_url):
        return jsonify({"error": "Unauthorized domain"}), 403
    
    try:
        # 从请求头中复制非敏感头部
        headers = {key: value for key, value in request.headers.items() 
                   if key not in ['Host', 'Set-Cookie']}
        # 设置模拟浏览器的User-Agent
        headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        # 发送请求到目标URL
        response = requests.get(
            target_url,
            headers=headers,
            cookies=request.cookies,
            allow_redirects=True,
            verify=False
        )
        
        # 创建代理响应对象
        proxy_response = make_response(response.content)
        proxy_response.status_code = response.status_code
        
        # 设置允许的响应头（排除安全限制和传输编码相关的头）
        excluded_headers = ['x-frame-options', 'content-security-policy', 'frame-options',
                           'transfer-encoding', 'content-encoding', 'content-length']
        for key, value in response.headers.items():
            if key.lower() not in excluded_headers:
                proxy_response.headers[key] = value
        
        # 设置CORS头部
        proxy_response.headers['Access-Control-Allow-Credentials'] = 'true'
        proxy_response.headers['Access-Control-Allow-Origin'] = '*'
        
        # 处理HTML内容，注入JavaScript
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' in content_type:
            content = response.content.decode('utf-8', errors='ignore')
            injected_js = """
<script>
    if(window.top!==window.self){Object.defineProperty(window,'top',{get:function(){return window.self;}});}
    Object.defineProperty(window,'parent',{get:function(){return window.self;}});
    Object.defineProperty(window,'frameElement',{get:function(){return null;}});
</script>
"""
            if '<head>' in content:
                content = content.replace('<head>', f'<head>{injected_js}')
            else:
                content = injected_js + content
            proxy_response.set_data(content.encode('utf-8'))
        
        return proxy_response
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def page_not_found(error):
    return render_template('index.html'), 404

def executecmd(command):
    proc=subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,universal_newlines=True)
    for line in iter(proc.stdout.readline,''):
        yield f"data:{line}\n\n"
    proc.stdout.close()
    proc.wait()
@app.route('/execute')
def execute():
    """执行命令前验证身份"""
    # 获取用户名和密码
    auth = request.authorization
    
    if not auth or not check_auth(auth.username, auth.password):
        # 需要身份验证
        return Response(
            "身份验证失败，请提供有效的用户名和密码",
            401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        )
    
    command = request.args.get('command')
    if not command:
        return Response("data:err:not any command\n\n", mimetype='text/event-stream')
    else:
        return Response(executecmd(command), mimetype='text/event-stream')

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

@app.route('/search-results')
def search_results():
    """渲染搜索结果页面，用于在iframe中显示"""
    return render_template('search_results.html')

@app.route('/search', methods=['POST'])
def search():
    """
    调用DeepSeek V4 Flash API进行搜索
    返回搜索结果，包含完整的URL显示
    """
    query = request.json.get('query')
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400
    
    if not DEEPSEEK_API_KEY:
        return jsonify({"error": "DeepSeek API key not configured"}), 500
    
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 构建搜索请求，要求返回包含URL的搜索结果
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个搜索引擎助手。请根据用户的查询进行搜索，并返回详细的搜索结果。每个搜索结果严格按照格式展示：标题；摘要；完整的URL链接。请用清晰的格式展示结果。"
                },
                {
                    "role": "user",
                    "content": f"请搜索以下内容并返回结果：{query}\n\n请确保每个搜索结果都包含完整的URL。"
                }
            ],
            "temperature": 0.0,
            "max_tokens": 2000
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, verify=False)
        response.raise_for_status()
        
        result = response.json()
        search_results = result.get('choices', [])[0].get('message', {}).get('content', '')
        
        return jsonify({"results": search_results})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/txt')
def txt():
    file_name = request.args.get('filename')
    file_path = os.path.join('txts', file_name)
    return send_from_directory('txts', file_name,mimetype='text/plain')


TEST_MODE = os.getenv("FLASK_TEST_MODE", "0") == "1"

if not TEST_MODE and not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit()
if __name__ == '__main__':
    while True:
        os.system('cls')
        print('欢迎')
        cert_path = os.path.join(os.path.dirname(__file__), 'cert.pem')
        key_path = os.path.join(os.path.dirname(__file__), 'key.pem')
        app.run(ssl_context=(cert_path, key_path), host=ip, port=443, threaded=True)
