from flask import Flask, request, jsonify, Response
import plotly.graph_objects as go
import json

app = Flask(__name__)

# Chart data and subscriber list
chart_data = {
    "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "revenues": [0] * 12
}
subscribers = []

def calculate_revenues(start_revenue, growth_rate):
    revenues = [start_revenue]
    for _ in range(11):
        revenues.append(revenues[-1] * (1 + growth_rate / 100))
    return revenues

def notify_subscribers():
    """Send updated chart data to all connected clients"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=chart_data["months"],
        y=chart_data["revenues"],
        mode="lines+markers",
        line=dict(color="blue")
    ))
    fig.update_layout(title="Live Revenue Projection")
    
    for subscriber in subscribers:
        subscriber(fig.to_json())

@app.route("/")
def chart():
    """Serves the chart page with SSE listener"""
    return f"""
    <html>
    <body>
        <div id="chart"></div>
        <script>
            const eventSource = new EventSource("/stream");
            eventSource.onmessage = (e) => {{
                const data = JSON.parse(e.data);
                Plotly.react("chart", data.data, data.layout);
            }};
        </script>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </body>
    </html>
    """

@app.route("/stream")
def stream():
    """SSE endpoint for real-time updates"""
    def event_stream():
        while True:
            yield f"data: {json.dumps(chart_data)}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

@app.route("/update", methods=["POST"])
def update():
    data = request.json
    chart_data["revenues"] = calculate_revenues(
        float(data["Revenue"]), 
        float(data["Growth Rate"])
    
    # Notify all connected clients
    notify_subscribers()
    return jsonify({"status": "Updated!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
