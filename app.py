import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key = os.environ.get('CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
    secure = True
)

class CommunityHubItem(db.Model):
    __tablename__ = 'community_hub_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    location = db.Column(db.String(100))
    date_event = db.Column(db.String(50))  # User input date
    contact = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    status = db.Column(db.String(20), default='Lost')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Background auto-delete tracker

with app.app_context():
    db.create_all()

def clean_expired_items():
    """Background helper to automatically delete entries older than 7 days"""
    try:
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        expired_items = CommunityHubItem.query.filter(CommunityHubItem.created_at < one_week_ago).all()
        for item in expired_items:
            db.session.delete(item)
        if expired_items:
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Auto-cleanup error: {e}")

@app.route('/', methods=['GET'])
def home():
    # Clean up old records every single time the home dashboard is requested
    clean_expired_items()
    
    items = CommunityHubItem.query.order_by(CommunityHubItem.id.desc()).all()
    lost_count = CommunityHubItem.query.filter_by(status='Lost').count()
    found_count = CommunityHubItem.query.filter_by(status='Found').count()
    return render_template('index.html', items=items, lost_count=lost_count, found_count=found_count)

@app.route('/report-lost', methods=['POST'])
def report_lost():
    try:
        item_name = request.form.get('itemName')
        category = request.form.get('category')
        description = request.form.get('description')
        location = request.form.get('location')
        date_event = request.form.get('date')
        contact = request.form.get('contact')
        status = request.form.get('status', 'Lost')
        
        image_file = request.files.get('image')
        image_url = None
        
        if image_file and image_file.filename != '':
            upload_result = cloudinary.uploader.upload(image_file)
            image_url = upload_result.get('secure_url')
        
        new_item = CommunityHubItem(
            name=item_name,
            category=category,
            description=description,
            location=location,
            date_event=date_event,
            contact=contact,
            image_url=image_url,
            status=status
        )
        db.session.add(new_item)
        db.session.commit()
        
        return redirect(url_for('home'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
