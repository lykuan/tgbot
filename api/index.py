from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Bot is running"})

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        return jsonify({"ok": True, "message": "Webhook endpoint is working"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# Vercel需要的handler
def handler(event, context):
    return app(event, context)

if __name__ == '__main__':
    app.run()
