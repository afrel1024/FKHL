from concurrent.futures import thread
import subprocess
from tokenize import Comment
from flask import Flask, Response, render_template,request,make_response,jsonify
import os
from flask_cors import CORS
import time
import requests
from urllib.parse import urlparse,urljoin
import sys
import ctypes
from python_hosts import Hosts,HostsEntry
ip=os.getenv("HOST_IP")

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
    proc.wait
@app.route('/execute')
def execute():
    command=request.args.get('command')
    if not command:
        return Response("data:err:not any command\n\n",mimetype='text/event-stream')
    else:
        return Response(executecmd(command),mimetype='text/event-stream')

##@app.errorhandler(404)
##def get_redirect():
##    return redirect('http://yandex.com',code=302,Response=None)
TEST_MODE = os.getenv("FLASK_TEST_MODE", "0") == "1"
if not TEST_MODE and not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit()
if __name__ == '__main__':
    while True:
        os.system('cls')
        print('欢迎')
        app.run(ssl_context=('cert.pem', 'key.pem'), host='127.0.0.1', port=5000,threaded=True)
        #app.run(host='192.168.137.1', port=80)
#bsource.weicistudy.com
