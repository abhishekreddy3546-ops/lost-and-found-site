import base64
import time
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Global list serving as our server application database storage
items_database = []

@app.route('/', methods=['GET'])
def home():
    # Capture search text query and active tab filters from URL params
    search_query = request.args.get('search', '').lower()
    active_filter = request.args.get('filter', 'all')
    
    filtered_items = []
    lost_count = 0
    found_count = 0
    
    # Process dataset calculations and text criteria match filters
    for item in items_database:
        if item['type'] == 'lost':
            lost_count += 1
        if item['type'] == 'found':
            found_count += 1
            
        # Tab toggle rule
        if active_filter != 'all' and item['type'] != active_filter:
            continue
            
        # Text criteria keyword match rule
        matches_search = (
            search_query in item['name'].lower() or 
            search_query in item['description'].lower() or 
            search_query in item['location'].lower()
        )
        if not matches_search:
            continue
            
        filtered_items.append(item)

    # Render layout targeting index.html explicitly
    return render_template(
        'index.html', 
        items=filtered_items, 
        total_count=len(items_database),
        lost_count=lost_count,
        found_count=found_count,
        search_query=search_query,
        active_filter=active_filter
    )

@app.route('/report-lost', methods=['POST'])
def report_lost():
    photo_file = request.files.get('lostPhoto')
    image_data_uri = None
    
    # Convert uploaded media files to base64 text uri data inside python
    if photo_file and photo_file.filename != '':
        encoded_string = base64.b64encode(photo_file.read()).decode('utf-8')
        image_data_uri = f"data:{photo_file.content_type};base64,{encoded_string}"
        
    new_item = {
        'id': int(time.time()),
        'type': 'lost',
        'name': request.form.get('lostName'),
        'category': request.form.get('lostCategory'),
        'description': request.form.get('lostDesc'),
        'location': request.form.get('lostLoc'),
        'date': request.form.get('lostDate'),
        'contact': request.form.get('lostContact'),
        'image': image_data_uri
    }
    
    items_database.insert(0, new_item)
    return redirect(url_for('home'))

@app.route('/report-found', methods=['POST'])
def report_found():
    new_item = {
        'id': int(time.time()),
        'type': 'found',
        'name': request.form.get('foundName'),
        'category': request.form.get('foundCategory'),
        'description': request.form.get('foundDesc'),
        'location': request.form.get('foundLoc'),
        'date': request.form.get('foundDate'),
        'contact': request.form.get('foundContact'),
        'image': None
    }
    
    items_database.insert(0, new_item)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)

