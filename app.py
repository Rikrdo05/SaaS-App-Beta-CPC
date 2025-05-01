from flask import Flask, request, jsonify
import plotly.graph_objects as go

app = Flask(__name__)

# Chart data
chart_data = {
    "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "revenues": [0] * 12
}

@app.route("/")
def home():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=chart_data["months"],
        y=chart_data["revenues"],
        mode="lines+markers"
    ))
    return fig.to_html()

@app.route("/update", methods=["POST"])
def update():
    data = request.json
    chart_data["revenues"] = [
        float(data["Revenue"]) * (1 + float(data["Growth Rate"])/100)**i 
        for i in range(12)
    ]
    return jsonify({"status": "Updated!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
