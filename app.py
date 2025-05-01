from flask import Flask, request, jsonify, Response, redirect
import plotly.graph_objects as go
import json
from threading import Lock
import time

app = Flask(__name__)
data_lock = Lock()

# Chart data storage
chart_data = {
    "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "revenues": None  # Initialize as empty
}

# --- Form Submission Handler ---
@app.route('/submit', methods=['GET', 'POST'])
def handle_form():
    if request.method == 'POST':
        try:
            revenue = float(request.form.get('revenue'))
            growth_rate = float(request.form.get('growth_rate')) / 100  # Convert % to decimal
            
            with data_lock:
                # Calculate compounded revenues
                chart_data["revenues"] = [
                    revenue * (1 + growth_rate)**i 
                    for i in range(12)
                ]
            
            return redirect('/')  # Redirect to the chart after submission
        
        except Exception as e:
            return f"Error: {str(e)}", 400
    
    # Show form if GET request
    return '''
    <form method="POST">
        <h2>Enter Projection Data</h2>
        Revenue ($): 
        <input type="number" name="revenue" step="0.01" required><br><br>
        Monthly Growth Rate (%): 
        <input type="number" name="growth_rate" step="0.01" required><br><br>
        <button type="submit">Update Chart</button>
    </form>
    '''

# --- Chart Display (with SSE for real-time updates) ---
@app.route('/')
def show_chart():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Revenue Projection</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #chart { width: 100%; height: 70vh; }
            a { color: #007BFF; text-decoration: none; }
        </style>
    </head>
    <body>
        <h1>Revenue Projection</h1>
        <a href="/submit">Edit Values</a>
        <div id="chart"></div>
        
        <script>
            // Initialize empty chart
            const layout = {
                title: 'Monthly Revenue',
                xaxis: { title: 'Month' },
                yaxis: { title: 'Revenue ($)' }
            };
            Plotly.newPlot('chart', [{
                x: [],
                y: [],
                type: 'scatter',
                mode: 'lines+markers'
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

# --- SSE Endpoint (unchanged) ---
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
