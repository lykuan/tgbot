import threading
import time
import http.server
import socketserver

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def log_message(self, format, *args):
        # 禁用日志输出
        pass

def run_keep_alive_server():
    """运行一个简单的HTTP服务器来保持脚本活跃"""
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Keep-alive server running on port {PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"Keep-alive server error: {e}")
        time.sleep(5)
        run_keep_alive_server()

def start_keep_alive():
    """在后台线程启动keep-alive服务器"""
    keep_alive_thread = threading.Thread(target=run_keep_alive_server, daemon=True)
    keep_alive_thread.start()
