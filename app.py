import os
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

class RegisteredItem(db.Model):
    __tablename__ = 'registered_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    location = db.Column(db.String(100))
    date = db.Column(db.String(50))
    contact = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    status = db.Column(db.String(20), default='Lost')

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/api/items', methods=['GET'])
def get_items():
    try:
        items_query = RegisteredItem.query.order_by(RegisteredItem.id.desc()).all()
        lost_count = RegisteredItem.query.filter_by(status='Lost').count()
        found_count = RegisteredItem.query.filter_by(status='Found').count()
        
        items_list = []
        for item in items_query:
            items_list.append({
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "location": item.location,
                "date": item.date,
                "contact": item.contact,
                "description": item.description,
                "image_url": item.image_url,
                "status": item.status
            })
            
        return jsonify({
            "items": items_list,
            "lost_count": lost_count,
            "found_count": found_count,
            "total_count": len(items_list)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/report-lost', methods=['POST'])
def report_lost():
    try:
        item_name = request.form.get('itemName')
        category = request.form.get('category')
        description = request.form.get('description')
        location = request.form.get('location')
        date = request.form.get('date')
        contact = request.form.get('contact')
        status = request.form.get('status', 'Lost')
        
        image_file = request.files.get('image')
        image_url = None
        
        if image_file and image_file.filename != '':
            upload_result = cloudinary.uploader.upload(image_file)
            image_url = upload_result.get('secure_url')
        
        new_item = RegisteredItem(
            name=item_name,
            category=category,
            description=description,
            location=location,
            date=date,
            contact=contact,
            image_url=image_url,
            status=status
        )
        db.session.add(new_item)
        db.session.commit()
        
        # FIXED: Return clean JSON status to allow JavaScript pipelines to execute updates
        return jsonify({
            "status": "success",
            "message": "Report logged cleanly in backend pipeline",
            "item_id": new_item.id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
