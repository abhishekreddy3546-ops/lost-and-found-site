from flask import Flask, render_template_string, request, redirect
import os
import base64

app = Flask(__name__)

# Shared memory database holding separate test items
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
    <title>{{ current_page.capitalize() }} Board - Last and Found</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 600px; margin: 40px auto; padding: 0 20px; background-color: #f9f9f9; color: #333; }
        h1 { text-align: center; color: #2c3e50; margin-bottom: 5px; }
        .tagline { text-align: center; color: #666; margin-bottom: 25px; }
        
        /* Navigation Links */
        .navigation { display: flex; justify-content: center; gap: 15px; margin-bottom: 30px; }
        .nav-link { padding: 12px 24px; background-color: #e0e0e0; color: #555; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 15px; transition: 0.2s; border-bottom: 4px solid #ccc; }
        .nav-link:hover { background-color: #d0d0d0; }
        .nav-link.active-lost { background-color: #e74c3c; color: white; border-bottom: 4px solid #c0392b; }
        .nav-link.active-found { background-color: #2ecc71; color: white; border-bottom: 4px solid #27ae60; }
        
        form { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 30px; border-top: 5px solid {{ theme_color }}; }
        input, textarea { width: 100%; padding: 10px; margin: 8px 0 16px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 14px; }
        textarea { height: 80px; resize: vertical; }
        
        button.submit-btn { width: 100%; background-color: {{ theme_color }}; color: white; padding: 12px; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; font-weight: bold; }
        button.submit-btn:hover { opacity: 0.9; }
        
        .card { background: white; border: 1px solid #ddd; padding: 20px; margin-top: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border-left: 6px solid {{ theme_color }}; }
        .status-badge { display: inline-block; padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; color: white; background-color: {{ theme_color }}; }
        .uploaded-img { max-width: 100%; max-height: 300px; border-radius: 6px; margin-top: 12px; display: block; object-fit: contain; }
        .meta-info { margin-top: 10px; font-size: 13px; color: #555; background: #f0f2f5; padding: 8px; border-radius: 4px; }
        .meta-info a { color: #3498db; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🕵️‍♂️ Last and Found</h1>
    <p class="tagline">A live notice board controlled instantly by everyone.</p>
    
    <!-- Navigation Panel to Switch Between Separate Places -->
    <div class="navigation">
        <a href="/lost" class="nav-link {% if current_page == 'lost' %}active-lost{% endif %}">🔴 Lost Board</a>
        <a href="/found" class="nav-link {% if current_page == 'found' %}active-found{% endif %}">🟢 Found Board</a>
    </div>
    
    <!-- Dynamic Form Based on Active Page Section -->
    <form action="/add/{{ current_page }}" method="POST" enctype="multipart/form-data">
        <h2 style="margin-top:0; color: {{ theme_color }};">Report a {{ current_page.capitalize() }} Item</h2>
        
        <label><b>Item Name</b></label>
        <input type="text" name="title" placeholder="What did you {{ 'lose' if current_page == 'lost' else 'find' }}?" required>
        
        <label><b>{{ 'Lost Place' if current_page == 'lost' else 'Found Place' }}</b></label>
        <input type="text" name="place" placeholder="Where was it {{ 'lost' if current_page == 'lost' else 'found' }}?" required>

        <label><b>Description</b></label>
        <textarea name="desc" placeholder="Provide extra details (Color, unique identifiers...)" required></textarea>
        
        <label><b>Upload a Photo (Optional)</b></label>
        <input type="file" name="item_photo" accept="image/*">
        
        <label><b>Contact Number</b></label>
        <input type="tel" name="contact_number" placeholder="Enter your contact number" required>
        
        <button type="submit" class="submit-btn">Submit to {{ current_page.capitalize() }} Board</button>
    </form>

    <h2>Active {{ current_page.capitalize() }} Bulletins</h2>
    
    {% if not items %}
    <p style="color: #999; font-style: italic;">No items posted here yet.</p>
    {% endif %}

    {% for item in items %}
    <div class="card">
        <h3>{{ item.title }} <span class="status-badge">{{ item.status }}</span></h3>
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
def index():
    # If someone visits the main root URL, automatically send them to the Lost page
    return redirect('/lost')

@app.route('/lost')
def lost_board():
    # Filter out only items that are Lost
    lost_items = [i for i in items_database if i['status'] == 'Lost']
    return render_template_string(HTML_TEMPLATE, items=lost_items, current_page='lost', theme_color='#e74c3c')

@app.route('/found')
def found_board():
    # Filter out only items that are Found
    found_items = [i for i in items_database if i['status'] == 'Found']
    return render_template_string(HTML_TEMPLATE, items=found_items, current_page='found', theme_color='#2ecc71')

@app.route('/add/<page_type>', methods=['POST'])
def add_item(page_type):
    photo_file = request.files.get('item_photo')
    image_base64_url = ""
    
    if photo_file and photo_file.filename != '':
        file_bytes = photo_file.read()
        encoded_string = base64.b64encode(file_bytes).decode('utf-8')
        image_base64_url = f"data:{photo_file.content_type};base64,{encoded_string}"

    # Automatically set the status tag based on what page path they sent it from
    status_tag = "Lost" if page_type == "lost" else "Found"

    new_post = {
        "title": request.form.get('title'),
        "status": status_tag,
        "place": request.form.get('place'),
        "description": request.form.get('desc'),
        "contact_number": request.form.get('contact_number') or "None Provided",
        "image_data": image_base64_url
    }
    
    items_database.insert(0, new_post)
    return redirect(f"/{page_type}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
