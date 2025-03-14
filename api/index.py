def handler(request, response):
    status = '200 OK'
    response_headers = [('Content-type', 'application/json')]
    response(status, response_headers)
    return [b'{"status": "Bot is running"}']

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, handler)
    print("Serving on port 8000...")
    httpd.serve_forever()
