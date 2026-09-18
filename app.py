import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 1. DATABASE CONFIGURATION
# Pulls the secret DATABASE_URL from Render environments. 
# Falls back to a local SQLite database for offline computer testing.
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 2. DATABASE MODEL (The Table structure)
class TrackedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'lost' or 'found'
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(150), nullable=True)
    date = db.Column(db.String(50), nullable=True)
    contact = db.Column(db.String(100), nullable=True)

# Automatically create the cloud/local tables if they don't exist
with app.app_context():
    db.create_all()

# 3. ROUTES
@app.route('/')
def index():
    # Query all records directly from the persistent database
    all_items = TrackedItem.query.order_by(TrackedItem.id.desc()).all()
    
    # Separate them so your template can filter them if needed
    lost_items = [item for item in all_items if item.status == 'lost']
    found_items = [item for item in all_items if item.status == 'found']
    
    # Pass them directly to your index.html file
    return render_template(
        'index.html', 
        items=all_items, 
        lost_items=lost_items, 
        found_items=found_items,
        total_count=len(all_items),
        lost_count=len(lost_items),
        found_count=len(found_items)
    )

@app.route('/submit-lost', methods=['POST'])
def submit_lost():
    new_item = TrackedItem(
        name=request.form.get('name'),
        category=request.form.get('category'),
        status='lost',
        description=request.form.get('description'),
        location=request.form.get('location'),
        date=request.form.get('date'),
        contact=request.form.get('contact')
    )
    db.session.add(new_item)
    db.session.commit()  # Saves securely to the database
    return redirect(url_for('index'))

@app.route('/submit-found', methods=['POST'])
def submit_found():
    new_item = TrackedItem(
        name=request.form.get('name'),
        category=request.form.get('category'),
        status='found',
        description=request.form.get('description'),
        location=request.form.get('location'),
        date=request.form.get('date'),
        contact=request.form.get('contact')
    )
    db.session.add(new_item)
    db.session.commit()  # Saves securely to the database
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
