from flask import Flask, request, jsonify, Response
import plotly.graph_objects as go
import json
from threading import Lock, Condition
import time

app = Flask(__name__)
data_lock = Lock()
update_condition = Condition()
clients = []

# Chart data
chart_data = {
    "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "revenues": [0] * 12
}

def event_stream(client_id):
    while True:
        with update_condition:
            update_condition.wait()  # Wait for updates
            with data_lock:
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
    <head>
        <title>Real-Time Revenue Chart</title>
    </head>
    <body>
        <div id="chart" style="width:900px; height:500px;"></div>
        <script>
            const chartDiv = document.getElementById('chart');
            // Initial plot
            Plotly.newPlot(chartDiv, [{
                x: [],
                y: [],
                type: 'scatter',
                mode: 'lines+markers',
                line: {color: '#007BFF'}
            }], {
                title: 'Real-Time Revenue Projection',
                xaxis: {title: 'Month'},
                yaxis: {title: 'Revenue ($)'}
            });
            
            // SSE connection
            const eventSource = new EventSource('/stream');
            eventSource.onmessage = function(e) {
                const data = JSON.parse(e.data);
                Plotly.react(chartDiv, [{
                    x: data.months,
                    y: data.revenues
                }], {
                    title: `Updated: ${new Date().toLocaleTimeString()}`
                });
            };
        </script>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </body>
    </html>
    """

@app.route("/stream")
def stream():
    client_id = time.time()
    return Response(event_stream(client_id), mimetype="text/event-stream")

@app.route("/update", methods=["POST"])
def update():
    data = request.json
    with data_lock:
        chart_data["revenues"] = [
            float(data["Revenue"]) * (1 + float(data["Growth Rate"])/100)**i 
            for i in range(12)
        ]
    with update_condition:
        update_condition.notify_all()  # Notify all clients
    return jsonify({"status": "Updated!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
