from flask import Flask, render_template_string, request, redirect
import os

app = Flask(__name__)

# This list stays in the server memory. Anyone visiting the site will see and edit this exact list!
items_database = [
    {"title": "Sample Golden Keys", "status": "Lost", "description": "Left near the central park entrance.", "reported_by": "System"}
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Last and Found</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 600px; margin: 40px auto; padding: 0 20px; background-color: #f9f9f9; color: #333; }
        h1 { text-align: center; color: #2c3e50; }
        form { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 30px; }
        input, select, textarea { width: 100%; padding: 10px; margin: 8px 0 16px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 14px; }
        textarea { height: 80px; resize: vertical; }
        button { width: 100%; background-color: #3498db; color: white; padding: 12px; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #2980b9; }
        .card { background: white; border: 1px solid #ddd; padding: 20px; margin-top: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .Lost { border-left: 6px solid #e74c3c; }
        .Found { border-left: 6px solid #2ecc71; }
        .status-badge { display: inline-block; padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; color: white; }
        .badge-Lost { background-color: #e74c3c; }
        .badge-Found { background-color: #2ecc71; }
    </style>
</head>
<body>
    <h1>🕵️‍♂️ Last and Found</h1>
    <p style="text-align: center; color: #666;">A live notice board controlled instantly by everyone.</p>
    
    <form action="/add" method="POST">
        <label><b>Item Name</b></label>
        <input type="text" name="title" placeholder="What did you lose or find?" required>
        
        <label><b>Status</b></label>
        <select name="status">
            <option value="Lost">Lost</option>
            <option value="Found">Found</option>
        </select>
        
        <label><b>Description</b></label>
        <textarea name="desc" placeholder="Provide details (Location, color, contact info...)" required></textarea>
        
        <label><b>Your Name</b></label>
        <input type="text" name="reported_by" placeholder="Anonymous">
        
        <button type="submit">Post to Live Board</button>
    </form>

    <h2>Live Bulletins:</h2>
    {% for item in items %}
    <div class="card {{ item.status }}">
        <h3>{{ item.title }} <span class="status-badge badge-{{ item.status }}">{{ item.status }}</span></h3>
        <p>{{ item.description }}</p>
        <small style="color: #7f8c8d;">Reported by: {{ item.reported_by }}</small>
    </div>
    {% endfor %}
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, items=items_database)

@app.route('/add', methods=['POST'])
def add_item():
    new_post = {
        "title": request.form.get('title'),
        "status": request.form.get('status'),
        "description": request.form.get('desc'),
        "reported_by": request.form.get('reported_by') or "Anonymous"
    }
    # Inserts the new post at the top of the list so everyone sees it first
    items_database.insert(0, new_post)
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
