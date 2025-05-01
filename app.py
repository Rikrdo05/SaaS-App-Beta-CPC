from flask import Flask, request, Response
import json
from threading import Lock
import time

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching
data_lock = Lock()

chart_data = {
    "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "revenues": None
}

@app.after_request
def add_headers(response):
    """Essential anti-lag headers for iframes"""
    response.headers["X-Frame-Options"] = "ALLOW-FROM *"
    response.headers["Content-Security-Policy"] = "frame-ancestors *"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        try:
            revenue = float(request.form['revenue'])
            growth = float(request.form['growth_rate'])/100
            
            with data_lock:
                chart_data['revenues'] = [revenue * (1+growth)**i for i in range(12)]
                
            # Return minimal response
            return '', 204
            
        except Exception as e:
            return str(e), 400

    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <script src="https://cdn.plot.ly/plotly-2.16.1.min.js"></script>
        <script>
        let chart = Plotly.newPlot('chart', [{
            x: [],
            y: [],
            type: 'scatter'
        }], {
            margin: {t:20, b:20}
        }, {responsive: true});
        
        function refresh() {
            fetch('/data')
                .then(r => r.json())
                .then(d => {
                    Plotly.react('chart', [{
                        x: d.months,
                        y: d.revenues || []
                    }], {}, {});
                });
        }
        
        // Aggressive polling (every 300ms)
        setInterval(refresh, 300);
        refresh(); // Initial load
        </script>
    </head>
    <body style="margin:0">
        <form onsubmit="event.preventDefault(); fetch('/', {
            method: 'POST',
            body: new FormData(this)
        }).then(refresh)">
            <input name="revenue" type="number" step="0.01" placeholder="Revenue" required>
            <input name="growth_rate" type="number" step="0.01" placeholder="Growth %" required>
            <button type="submit">Update</button>
        </form>
        <div id="chart" style="width:100%;height:80vh"></div>
    </body>
    </html>
    '''

@app.route('/data')
def get_data():
    with data_lock:
        return json.dumps(chart_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
