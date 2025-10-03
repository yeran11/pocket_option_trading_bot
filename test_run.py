"""
Simple test to verify RUN button works
"""
print("=" * 60)
print("✅ RUN BUTTON IS WORKING!")
print("=" * 60)
print()
print("This proves the RUN button executes code.")
print()
print("Starting Flask web server...")
print()

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <head><title>IT WORKS!</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1 style="color: green;">✅ RUN BUTTON WORKS!</h1>
        <h2>🎉 Flask Web Server is Running!</h2>
        <p>The Pocket Option Trading Bot web interface is ready.</p>
        <p><a href="/" style="color: blue;">Refresh this page</a></p>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("🌐 Starting web server on port 5000...")
    print("📱 Check the webview panel or click the URL above!")
    print()
    app.run(host='0.0.0.0', port=5000, debug=False)
