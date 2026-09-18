import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback_local_secret_dev_key_123')

# Database Configuration (Fixes the Render Postgres URL naming scheme automatically)
db_url = os.environ.get('DATABASE_URL', 'sqlite:///local_lost_found.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model for Items
class LostFoundItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False) # 'Lost' or 'Found'
    location = db.Column(db.String(100), nullable=False)
    date_event = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables automatically
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    items = LostFoundItem.query.order_by(LostFoundItem.created_at.desc()).all()
    return render_template('index.html', items=items)

@app.route('/report', methods=['POST'])
def report_item():
    title = request.form.get('title')
    description = request.form.get('description')
    status = request.form.get('status')
    location = request.form.get('location')
    date_event = request.form.get('date_event') or 'Not provided'
    
    if not title or not description or not status or not location:
        flash("All main fields are required!", "danger")
        return redirect(url_for('index'))
        
    new_item = LostFoundItem(
        title=title,
        description=description,
        status=status,
        location=location,
        date_event=date_event
    )
    
    try:
        db.session.add(new_item)
        db.session.commit()
        flash("Report submitted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Database saving error. Please try again.", "danger")
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
