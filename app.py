from flask import Flask, request, jsonify, Response
import plotly.graph_objects as go
import json
from threading import Lock

app = Flask(__name__)
lock = Lock()

# Chart data
chart_data = {
    "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "revenues": [0] * 12
}

def event_stream():
    while True:
        with lock:
            data = json.dumps({
                "months": chart_data["months"],
                "revenues": chart_data["revenues"]
            })
        yield f"data: {data}\n\n"

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <body>
        <div id="chart"></div>
        <script>
            const evtSource = new EventSource("/stream");
            evtSource.onmessage = (e) => {
                const data = JSON.parse(e.data);
                Plotly.newPlot("chart", [{
                    x: data.months,
                    y: data.revenues,
                    type: 'scatter'
                }], {
                    title: 'Real-Time Revenue',
                    xaxis: {title: 'Month'},
                    yaxis: {title: 'Revenue ($)'}
                });
            };
        </script>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </body>
    </html>
    """

@app.route("/stream")
def stream():
    return Response(event_stream(), mimetype="text/event-stream")

@app.route("/update", methods=["POST"])
def update():
    data = request.json
    with lock:
        chart_data["revenues"] = [
            float(data["Revenue"]) * (1 + float(data["Growth Rate"])/100)**i
            for i in range(12)
        ]
    return jsonify({"status": "Updated!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
