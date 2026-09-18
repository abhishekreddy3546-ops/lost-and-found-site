from flask import Flask, render_template_string, request, redirect
import os
import base64

app = Flask(__name__)

# This database holds all sample posts in memory
items_database = [
    {
        "title": "Sample Golden Ring", 
        "status": "Lost", 
        "description": "Gold band with a small gemstone inscription.", 
        "contact_number": "+1234567890",
        "place": "Central Station Food Court",
        "image_data": ""
    },
    {
        "title": "Black Leather Wallet", 
        "status": "Found", 
        "description": "Found on the bus bench containing ID cards.", 
        "contact_number": "+9876543210",
        "place": "Downtown Bus Stop",
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
        h1 { text-align: center; color: #2c3e50; margin-bottom: 5px; }
        .tagline { text-align: center; color: #666; margin-bottom: 25px; }
        
        /* Navigation Tabs Style */
        .tabs { display: flex; justify-content: center; gap: 10px; margin-bottom: 30px; }
        .tab-btn { padding: 10px 20px; background-color: #e0e0e0; color: #555; text-decoration: none; border-radius: 20px; font-weight: bold; font-size: 14px; transition: 0.2s; }
        .tab-btn:hover { background-color: #d0d0d0; }
        .tab-btn.active { background-color: #3498db; color: white; }
        
        form { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 30px; }
        input, select, textarea { width: 100%; padding: 10px; margin: 8px 0 16px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 14px; }
        textarea { height: 80px; resize: vertical; }
        button.submit-btn { width: 100%; background-color: #2ecc71; color: white; padding: 12px; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; font-weight: bold; }
        button.submit-btn:hover { background-color: #27ae60; }
        
        .card { background: white; border: 1px solid #ddd; padding: 20px; margin-top: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .Lost { border-left: 6px solid #e74c3c; }
        .Found { border-left: 6px solid #2ecc71; }
        .status-badge { display: inline-block; padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; color: white; }
        .badge-Lost { background-color: #e74c3c; }
        .badge-Found { background-color: #2ecc71; }
        .uploaded-img { max-width: 100%; max-height: 300px; border-radius: 6px; margin-top: 12px; display: block; object-fit: contain; }
        .meta-info { margin-top: 10px; font-size: 13px; color: #555; background: #f0f2f5; padding: 8px; border-radius: 4px; }
        .meta-info a { color: #3498db; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🕵️‍♂️ Last and Found</h1>
    <p class="tagline">A live notice board controlled instantly by everyone.</p>
    
    <!-- Top Board Filter Tabs -->
    <div class="tabs">
        <a href="/" class="tab-btn {% if current_filter == 'all' %}active{% endif %}">📋 All Items</a>
        <a href="/?filter=Lost" class="tab-btn {% if current_filter == 'Lost' %}active{% endif %}">🔴 Lost Items</a>
        <a href="/?filter=Found" class="tab-btn {% if current_filter == 'Found' %}active{% endif %}">🟢 Found Items</a>
    </div>
    
    <!-- Submission Form -->
    <form action="/add" method="POST" enctype="multipart/form-data">
        <label><b>Item Name</b></label>
        <input type="text" name="title" placeholder="What did you lose or find?" required>
        
        <label><b>Status</b></label>
        <select name="status" id="statusSelect" onchange="updateLocationLabel()">
            <option value="Lost">Lost</option>
            <option value="Found">Found</option>
        </select>
        
        <label><b id="locationLabel">Lost Place</b></label>
        <input type="text" name="place" id="placeInput" placeholder="Where was it lost?" required>

        <label><b>Description</b></label>
        <textarea name="desc" placeholder="Provide extra details (Color, shape, distinctive markers...)" required></textarea>
        
        <label><b>Upload a Photo of the Item (Optional)</b></label>
        <input type="file" name="item_photo" accept="image/*">
        
        <label><b>Contact Number</b></label>
        <input type="tel" name="contact_number" placeholder="Enter phone number to reach you" required>
        
        <button type="submit" class="submit-btn">Post to Live Board</button>
    </form>

    <h2>Showing: {{ current_filter.capitalize() }} Bulletins</h2>
    
    {% if not items %}
    <p style="color: #999; font-style: italic;">No items posted in this category yet.</p>
    {% endif %}

    {% for item in items %}
    <div class="card {{ item.status }}">
        <h3>{{ item.title }} <span class="status-badge badge-{{ item.status }}">{{ item.status }}</span></h3>
        <p>{{ item.description }}</p>
        
        {% if item.image_data %}
        <img class="uploaded-img" src="{{ item.image_data }}" alt="Uploaded item photo">
        {% endif %}
        
        <div class="meta-info">
            📍 <b>Location:</b> {{ item.place }}<br>
            📞 <b>Contact Number:</b> [{{ item.contact_number }}](tel:{{ item.contact_number }})
        </div>
    </div>
    {% endfor %}

    <script>
    function updateLocationLabel() {
        var status = document.getElementById("statusSelect").value;
        var label = document.getElementById("locationLabel");
        var input = document.getElementById("placeInput");
        
        if (status === "Lost") {
            label.innerHTML = "Lost Place";
            input.placeholder = "Where was it lost?";
        } else {
            label.innerHTML = "Found Place";
            input.placeholder = "Where was it found?";
        }
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    # Read the ?filter= parameter from the website URL address
    category_filter = request.args.get('filter', 'all')
    
    if category_filter in ['Lost', 'Found']:
        # Filter items list down to just matches
        filtered_items = [i for i in items_database if i['status'] == category_filter]
    else:
        filtered_items = items_database
        
    return render_template_string(HTML_TEMPLATE, items=filtered_items, current_filter=category_filter)

@app.route('/add', methods=['POST'])
def add_item():
    photo_file = request.files.get('item_photo')
    image_base64_url = ""
    
    if photo_file and photo_file.filename != '':
        file_bytes = photo_file.read()
        encoded_string = base64.b64encode(file_bytes).decode('utf-8')
        image_base64_url = f"data:{photo_file.content_type};base64,{encoded_string}"

    new_post = {
        "title": request.form.get('title'),
        "status": request.form.get('status'),
        "place": request.form.get('place'),
        "description": request.form.get('desc'),
        "contact_number": request.form.get('contact_number') or "None Provided",
        "image_data": image_base64_url
    }
    
    items_database.insert(0, new_post)
    
    # Redirect back to the exact list they just posted to
    return redirect(f"/?filter={new_post['status']}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
