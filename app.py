from flask import Flask, render_template_string, request, redirect
import os
import base64

app = Flask(__name__)

# This database holds the posts in the server's memory
items_database = [
    {
        "title": "Example Wallet", 
        "status": "Found", 
        "description": "Found a brown leather wallet near the bus stop.", 
        "reported_by": "System",
        "image_data": ""
    }
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
        .uploaded-img { max-width: 100%; max-height: 300px; border-radius: 6px; margin-top: 12px; display: block; object-fit: contain; }
    </style>
</head>
<body>
    <h1>🕵️‍♂️ Last and Found</h1>
    <p style="text-align: center; color: #666;">A live notice board controlled instantly by everyone.</p>
    
    <!-- Using multipart/form-data to allow real image uploading -->
    <form action="/add" method="POST" enctype="multipart/form-data">
        <label><b>Item Name</b></label>
        <input type="text" name="title" placeholder="What did you lose or find?" required>
        
        <label><b>Status</b></label>
        <select name="status">
            <option value="Lost">Lost</option>
            <option value="Found">Found</option>
        </select>
        
        <label><b>Description</b></label>
        <textarea name="desc" placeholder="Provide details (Location, color, contact info...)" required></textarea>
        
        <label><b>Upload a Photo of the Item (Optional)</b></label>
        <input type="file" name="item_photo" accept="image/*">
        
        <label><b>Your Name</b></label>
        <input type="text" name="reported_by" placeholder="Anonymous">
        
        <button type="submit">Post to Live Board</button>
    </form>

    <h2>Live Bulletins:</h2>
    {% for item in items %}
    <div class="card {{ item.status }}">
        <h3>{{ item.title }} <span class="status-badge badge-{{ item.status }}">{{ item.status }}</span></h3>
        <p>{{ item.description }}</p>
        
        <!-- Displays the uploaded photo if one exists -->
        {% if item.image_data %}
        <img class="uploaded-img" src="{{ item.image_data }}" alt="Uploaded item photo">
        {% endif %}
        
        <br>
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
    photo_file = request.files.get('item_photo')
    image_base64_url = ""
    
    # Process the uploaded image file and convert it into a string to store it safely
    if photo_file and photo_file.filename != '':
        file_bytes = photo_file.read()
        encoded_string = base64.b64encode(file_bytes).decode('utf-8')
        image_base64_url = f"data:{photo_file.content_type};base64,{encoded_string}"

    new_post = {
        "title": request.form.get('title'),
        "status": request.form.get('status'),
        "description": request.form.get('desc'),
        "reported_by": request.form.get('reported_by') or "Anonymous",
        "image_data": image_base64_url
    }
    
    items_database.insert(0, new_post)
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
