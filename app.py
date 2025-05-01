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
    """Handle form submission and serve interface"""
    if request.method == 'POST':
        try:
            start_time = time.time()
            revenue = float(request.form.get('revenue'))
            growth_rate = float(request.form.get('growth_rate')) / 100
            
            with data_lock:
                chart_data["revenues"] = [
                    revenue * (1 + growth_rate)**i 
                    for i in range(12)
                ]
            
            print(f"Processed in {(time.time() - start_time)*1000:.1f}ms")
        except Exception as e:
            return f"Error: {str(e)}", 400

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
            input, button { padding: 8px; margin: 5px 0; width: 200px; }
            button { background: #007BFF; color: white; border: none; cursor: pointer; }
            label { display: inline-block; width: 150px; }
        </style>
    </head>
    <body>
        <h1>Revenue Projection Tool</h1>
        
        <div id="form-container">
            <form method="POST">
                <h3>Enter Projection Data</h3>
                <div>
                    <label for="revenue">Starting Revenue ($):</label>
                    <input type="number" id="revenue" name="revenue" step="0.01" required>
                </div>
                <div>
                    <label for="growth_rate">Monthly Growth Rate (%):</label>
                    <input type="number" id="growth_rate" name="growth_rate" step="0.01" required>
                </div>
                <button type="submit">Update Projection</button>
            </form>
        </div>

        <div id="chart"></div>
        
        <script>
            // Optimized Plotly configuration
            const config = {
                responsive: true,
                displayModeBar: false,
                staticPlot: false
            };
            
            const layout = {
                title: 'Monthly Revenue Projection',
                xaxis: { title: 'Month' },
                yaxis: { title: 'Revenue ($)' },
                margin: { t: 40, b: 40, l: 60, r: 20 }
            };
            
            // Initialize empty chart
            let chart = Plotly.newPlot('chart', [{
                x: [],
                y: [],
                type: 'scatter',
                mode: 'lines+markers',
                line: { color: '#007BFF' }
            }], layout, config);

            // High-performance SSE connection
            const eventSource = new EventSource('/stream');
            let lastUpdate = 0;
            
            eventSource.onmessage = (e) => {
                const now = Date.now();
                if (now - lastUpdate < 100) return; // Throttle to 100ms
                lastUpdate = now;
                
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
    """Optimized SSE endpoint"""
    def generate():
        last_data = None
        while True:
            with data_lock:
                current_data = json.dumps({
                    "months": chart_data["months"],
                    "revenues": chart_data["revenues"]
                })
            
            if current_data != last_data:
                yield f"data: {current_data}\n\n"
                last_data = current_data
            
            time.sleep(0.05)  # 50ms delay (reduced from 100ms)
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'X-Accel-Buffering': 'no',
            'Cache-Control': 'no-cache'
        }
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
