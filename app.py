from flask import Flask, request, jsonify, Response
import plotly.graph_objects as go
import json
from threading import Lock
import time

app = Flask(__name__)
data_lock = Lock()

# Default chart data
chart_data = {
    "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "revenues": [1000] * 12  # Default starting value
}

@app.route('/')
def home():
    """Serve the chart page with auto-updating JavaScript"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Real-Time Revenue Chart</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #chart { width: 100%; height: 80vh; }
        </style>
    </head>
    <body>
        <h1>Revenue Projection</h1>
        <div id="chart"></div>
        
        <script>
            // Initialize chart
            const layout = {
                title: 'Monthly Revenue (Live Updates)',
                xaxis: { title: 'Month' },
                yaxis: { title: 'Revenue ($)' },
                showlegend: false
            };
            
            let chart = Plotly.newPlot('chart', [{
                x: [],
                y: [],
                type: 'scatter',
                mode: 'lines+markers',
                line: { color: '#007BFF' }
            }], layout);

            // Connect to Server-Sent Events
            const eventSource = new EventSource('/stream');
            
            eventSource.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                Plotly.react('chart', [{
                    x: data.months,
                    y: data.revenues
                }], layout);
                
                console.log('Chart updated at:', new Date());
            };
        </script>
    </body>
    </html>
    """

@app.route('/stream')
def stream():
    """Server-Sent Events endpoint for real-time updates"""
    def generate():
        while True:
            with data_lock:
                data = json.dumps({
                    "months": chart_data["months"],
                    "revenues": chart_data["revenues"]
                })
            yield f"data: {data}\n\n"
            time.sleep(1)  # Prevent excessive updates
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/update', methods=['POST'])
def update():
    """Endpoint for Tally form submissions"""
    try:
        data = request.json
        with data_lock:
            # Calculate all months' revenues
            chart_data["revenues"] = [
                float(data["Revenue"]) * (1 + float(data["Growth Rate"])/100)**i 
                for i in range(12)
            ]
        
        return jsonify({"status": "Updated successfully"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
