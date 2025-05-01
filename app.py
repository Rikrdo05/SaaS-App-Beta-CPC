from flask import Flask, request, jsonify
import plotly.graph_objects as go
from threading import Lock

app = Flask(__name__)
lock = Lock()

# Chart data
chart_data = {
    "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "revenues": [0] * 12
}

def calculate_revenues(start_revenue, growth_rate):
    revenues = [start_revenue]
    for _ in range(11):
        revenues.append(revenues[-1] * (1 + growth_rate / 100))
    return revenues

@app.route("/")
def chart():
    with lock:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=chart_data["months"],
            y=chart_data["revenues"],
            mode="lines+markers",
            line=dict(color="blue")
        ))
        return fig.to_html()

@app.route("/update", methods=["POST"])
def update():
    data = request.json
    with lock:
        chart_data["revenues"] = calculate_revenues(
            float(data["Revenue"]), 
            float(data["Growth Rate"])
    return jsonify({"status": "Updated!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
