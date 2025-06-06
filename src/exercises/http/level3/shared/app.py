from flask import Flask, request, send_file, render_template_string
import os

app = Flask(__name__)
BASE_DIR = os.path.abspath(".")

@app.route("/", methods=["GET"])
def index():
    filename = request.args.get("file")

    if not filename:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>File Viewer</title>
            <style>
                body {
                    background-color: #2c001e;
                    color: #e0e0e0;
                    font-family: 'Courier New', Courier, monospace;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                }
                h1 {
                    color: #ff79c6;
                }
                form {
                    margin-top: 20px;
                }
                input {
                    padding: 8px;
                    background: #1c0014;
                    border: 1px solid #555;
                    color: #eee;
                    width: 300px;
                    font-family: inherit;
                }
                button {
                    background: #5e005c;
                    color: #fff;
                    border: none;
                    padding: 8px 16px;
                    margin-left: 8px;
                    cursor: pointer;
                }
                button:hover {
                    background: #ff79c6;
                    color: #000;
                }
            </style>
        </head>
        <body>
            <h1>📂 File Access Portal</h1>
            <form method="get">
                <input name="file" placeholder="enter file or directory" />
                <button type="submit">Open</button>
            </form>
        </body>
        </html>
        """)

    try:
        filepath = os.path.abspath(os.path.join(BASE_DIR, filename))
        return send_file(filepath)
    except Exception as e:
        return f"<pre style='color: #ff5555; background-color: #1c0014; padding: 20px;'>{str(e)}</pre>", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    

