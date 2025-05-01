from flask import Flask, request, jsonify
import plotly.graph_objects as go

app = Flask(__name__)

# Default data (will be overwritten by Tally)
chart_data = {
    "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "revenues": [0] * 12  # Placeholder (12 zeros)
}

def calculate_revenues(start_revenue, growth_rate):
    """Calculate monthly revenues based on growth rate"""
    revenues = [start_revenue]
    for _ in range(11):  # Next 11 months
        revenues.append(revenues[-1] * (1 + growth_rate / 100))
    return revenues

@app.route("/")
def chart():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=chart_data["months"],
        y=chart_data["revenues"],
        mode="lines+markers",
        line=dict(color="blue")
    ))
    fig.update_layout(
        title="Monthly Revenue Projection",
        xaxis_title="Month",
        yaxis_title="Revenue ($)"
    )
    return fig.to_html()

@app.route("/update", methods=["POST"])
def update():
    data = request.json
    # Updated to match Tally's EXACT field names (capitalized + space)
    jan_revenue = float(data["Revenue"])  # From Tally (capital "R")
    growth_rate = float(data["Growth Rate"])  # From Tally (capital "G" and space)
    
    # Calculate all months' revenues
    chart_data["revenues"] = calculate_revenues(jan_revenue, growth_rate)
    return jsonify({"status": "Updated!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
