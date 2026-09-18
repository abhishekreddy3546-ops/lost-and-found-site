import os
from flask import Flask, request, jsonify, render_template
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key = os.environ.get('CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
    secure = True
)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/report-lost', methods=['POST'])
def report_lost():
    try:
        item_name = request.form.get('itemName')
        description = request.form.get('description')
        
        image_file = request.files.get('image')
        image_url = None
        
        if image_file:
            upload_result = cloudinary.uploader.upload(image_file)
            image_url = upload_result.get('secure_url')
        
        return jsonify({
            "status": "success",
            "message": "Item reported successfully!", 
            "imageUrl": image_url
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
