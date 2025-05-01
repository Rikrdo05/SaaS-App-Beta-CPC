from flask import Flask, request, jsonify, Response
import plotly.graph_objects as go
import json
from threading import Lock
import time

app = Flask(__name__)
data_lock = Lock()

# Initialize with empty data
chart_data = {
    "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "revenues": None
}

@app.route('/', methods=['GET', 'POST'])
def home():
    # Handle form submission
    if request.method == 'POST':
        try:
            revenue = float(request.form.get('revenue'))
            growth_rate = float(request.form.get('growth_rate')) / 100  # Convert % to decimal
            
            with data_lock:
                chart_data["revenues"] = [
                    revenue * (1 + growth_rate)**i 
                    for i in range(12)
                ]
        except Exception as e:
            return f"Error: {str(e)}", 400

    # Serve the combined interface
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Revenue Projection</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            #form-container { background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            #chart { width: 100%; height: 500px; margin-top: 20px; }
            input, button { padding: 8px; margin: 5px 0; }
            button { background: #007BFF; color: white; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Revenue Projection Tool</h1>
        
        <div id="form-container">
            <form method="POST">
                <h3>Enter Projection Data</h3>
                <div>
                    <label>Starting Revenue ($):</label>
                    <input type="number" name="revenue" step="0.01" required>
                </div>
                <div>
                    <label>Monthly Growth Rate (%):</label>
                    <input type="number" name="growth_rate" step="0.01" required>
                </div>
                <button type="submit">Update Projection</button>
            </form>
        </div>

        <div id="chart"></div>
        
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

            // Real-time updates via SSE
            const eventSource = new EventSource('/stream');
            eventSource.onmessage = (e) => {
                const data = JSON.parse(e.data);
                if (data.revenues) {
                    Plotly.react('chart', [{
                        x: data.months,
                        y: data.revenues
                    }], layout);
                }
            };
        </script>
    </body>
    </html>
    '''

@app.route('/stream')
def stream():
    def generate():
        while True:
            with data_lock:
                data = json.dumps({
                    "months": chart_data["months"],
                    "revenues": chart_data["revenues"]
                })
            yield f"data: {data}\n\n"
            time.sleep(0.1)
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
