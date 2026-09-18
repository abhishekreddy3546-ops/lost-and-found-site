from flask import Flask, render_template_string, request, redirect
import os
import base64

app = Flask(__name__)

# The database is now completely empty, ready for live entries!
items_database = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Last and Found</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; background-color: #f9f9f9; color: #333; }
        h1 { text-align: center; color: #2c3e50; margin-bottom: 5px; }
        .tagline { text-align: center; color: #666; margin-bottom: 30px; }
        
        /* Container to place the two forms side-by-side on desktop */
        .forms-container { display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 40px; }
        .form-box { flex: 1; min-width: 300px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); box-sizing: border-box; }
        
        .lost-box { border-top: 6px solid #e74c3c; }
        .found-box { border-top: 6px solid #2ecc71; }
        
        h3 { margin-top: 0; margin-bottom: 15px; }
        .lost-title { color: #e74c3c; }
        .found-title { color: #2ecc71; }
        
        input, textarea { width: 100%; padding: 8px; margin: 6px 0 12px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 14px; }
        textarea { height: 60px; resize: vertical; }
        
        button { width: 100%; color: white; padding: 10px; border: none; border-radius: 4px; font-size: 15px; cursor: pointer; font-weight: bold; }
        .lost-btn { background-color: #e74c3c; }
        .lost-btn:hover { background-color: #c0392b; }
        .found-btn { background-color: #2ecc71; }
        .found-btn:hover { background-color: #27ae60; }
        
        /* Combined Feed Styling */
        .feed-heading { border-bottom: 2px solid #ddd; padding-bottom: 10px; margin-top: 40px; color: #2c3e50; }
        .card { background: white; border: 1px solid #ddd; padding: 20px; margin-top: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .card.Lost { border-left: 6px solid #e74c3c; }
        .card.Found { border-left: 6px solid #2ecc71; }
        
        .status-badge { display: inline-block; padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; color: white; }
        .badge-Lost { background-color: #e74c3c; }
        .badge-Found { background-color: #2ecc71; }
        
        .uploaded-img { max-width: 100%; max-height: 250px; border-radius: 6px; margin-top: 12px; display: block; object-fit: contain; }
        .meta-info { margin-top: 10px; font-size: 13px; color: #555; background: #f0f2f5; padding: 8px; border-radius: 4px; line-height: 1.5; }
        .meta-info a { color: #3498db; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🕵️‍♂️ Last and Found</h1>
    <p class="tagline">Controlled instantly by everyone. Post your item below.</p>
    
    <div class="forms-container">
        <!-- 🔴 Separate Entry for Lost Items -->
        <div class="form-box lost-box">
            <h3 class="lost-title">🔴 Report a Lost Item</h3>
            <form action="/add/Lost" method="POST" enctype="multipart/form-data" style="box-shadow:none; padding:0;">
                <label><b>Item Name</b></label>
                <input type="text" name="title" placeholder="What did you lose?" required>
                
                <label><b>Lost Place</b></label>
                <input type="text" name="place" placeholder="Where was it last seen?" required>

                <label><b>Description</b></label>
                <textarea name="desc" placeholder="Color, brand, special marks..." required></textarea>
                
                <label><b>Photo (Optional)</b></label>
                <input type="file" name="item_photo" accept="image/*">
                
                <label><b>Contact Number</b></label>
                <input type="tel" name="contact_number" placeholder="Your phone number" required>
                
                <button type="submit" class="lost-btn">Submit Lost Report</button>
            </form>
        </div>

        <!-- 🟢 Separate Entry for Found Items -->
        <div class="form-box found-box">
            <h3 class="found-title">🟢 Report a Found Item</h3>
            <form action="/add/Found" method="POST" enctype="multipart/form-data" style="box-shadow:none; padding:0;">
                <label><b>Item Name</b></label>
                <input type="text" name="title" placeholder="What did you find?" required>
                
                <label><b>Found Place</b></label>
                <input type="text" name="place" placeholder="Where did you spot it?" required>

                <label><b>Description</b></label>
                <textarea name="desc" placeholder="Describe the item condition..." required></textarea>
                
                <label><b>Photo (Optional)</b></label>
                <input type="file" name="item_photo" accept="image/*">
                
                <label><b>Contact Number</b></label>
                <input type="tel" name="contact_number" placeholder="Your phone number" required>
                
                <button type="submit" class="found-btn">Submit Found Report</button>
            </form>
        </div>
    </div>

    <!-- 📋 Combined Live Bulletin Feed -->
    <h2 class="feed-heading">📋 Live Bulletins (Lost & Found Combined)</h2>
    
    {% if not items %}
    <p style="color: #999; font-style: italic; text-align: center; margin-top: 30px;">The notice board is currently empty. Be the first to report an item!</p>
    {% endif %}

    {% for item in items %}
    <div class="card {{ item.status }}">
        <h3>{{ item.title }} <span class="status-badge badge-{{ item.status }}">{{ item.status }}</span></h3>
        <p>{{ item.description }}</p>
        
        {% if item.image_data %}
        <img class="uploaded-img" src="{{ item.image_data }}" alt="Item photo">
        {% endif %}
        
        <div class="meta-info">
            📍 <b>{{ 'Lost Place' if item.status == 'Lost' else 'Found Place' }}:</b> {{ item.place }}<br>
            📞 <b>Contact Number:</b> <a href="tel:{{ item.contact_number }}">{{ item.contact_number }}</a>
        </div>
    </div>
    {% endfor %}
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, items=items_database)

@app.route('/add/<status_type>', methods=['POST'])
def add_item(status_type):
    photo_file = request.files.get('item_photo')
    image_base64_url = ""
    
    if photo_file and photo_file.filename != '':
        file_bytes = photo_file.read()
        encoded_string = base64.b64encode(file_bytes).decode('utf-8')
        image_base64_url = f"data:{photo_file.content_type};base64,{encoded_string}"

    new_post = {
        "title": request.form.get('title'),
        "status": status_type,
        "place": request.form.get('place'),
        "description": request.form.get('desc'),
        "contact_number": request.form.get('contact_number') or "None Provided",
        "image_data": image_base64_url
    }
    
    items_database.insert(0, new_post)
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
