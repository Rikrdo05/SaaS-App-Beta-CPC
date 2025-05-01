from flask import Flask, request, jsonify, Response
import plotly.graph_objects as go
import json
from threading import Lock
import time

app = Flask(__name__)
data_lock = Lock()

# Start with empty data
chart_data = {
    "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "revenues": None  # Will be set by first Tally submission
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
            #status { color: #666; margin-top: 10px; }
        </style>
    </head>
    <body>
        <h1>Revenue Projection</h1>
        <div id="chart"></div>
        <div id="status">Waiting for first data submission...</div>
        
        <script>
            // Initialize empty chart
            const layout = {
                title: 'Monthly Revenue Projection',
                xaxis: { title: 'Month' },
                yaxis: { title: 'Revenue ($)' }
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
                const statusEl = document.getElementById('status');
                
                if (data.revenues) {
                    Plotly.react('chart', [{
                        x: data.months,
                        y: data.revenues
                    }], layout);
                    statusEl.textContent = `Last updated: ${new Date().toLocaleString()}`;
                    statusEl.style.color = 'green';
                }
            };
        </script>
    </body>
    </html>
    """

@app.route('/stream')
def stream():
    """Server-Sent Events endpoint"""
    def generate():
        while True:
            with data_lock:
                data = json.dumps({
                    "months": chart_data["months"],
                    "revenues": chart_data["revenues"]
                })
            yield f"data: {data}\n\n"
            time.sleep(0.5)  # Prevent excessive updates
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/update', methods=['POST'])
def update():
    """Handle Tally form submissions"""
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
