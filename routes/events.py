from flask import Blueprint, request, jsonify, send_file
from models import db, Event
from datetime import datetime, date
import pytz
import os
from werkzeug.utils import secure_filename
import secrets

bp = Blueprint('events', __name__, url_prefix='/api/events')

ADMIN_PASSWORD = 'Elim@2025'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def check_auth():
    password = request.headers.get('X-ADMIN-PASSWORD')
    if password != ADMIN_PASSWORD:
        return False
    return True

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload(file, app):
    if not allowed_file(file.filename):
        raise ValueError('Invalid file extension')
    
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    rand = secrets.token_hex(3)
    fname = secure_filename(file.filename)
    new_filename = f"{ts}__{rand}__{fname}"
    
    upload_path = os.path.join(app.root_path, 'static', 'uploads', new_filename)
    file.save(upload_path)
    
    return f"/static/uploads/{new_filename}"

def get_today():
    tz = pytz.timezone('Africa/Nairobi')
    return datetime.now(tz).date()

@bp.route('', methods=['GET'])
def get_all_events():
    events = Event.query.all()
    return jsonify([event.to_dict() for event in events])

@bp.route('/upcoming', methods=['GET'])
def get_upcoming_events():
    today = get_today()
    events = Event.query.filter(Event.date >= today).order_by(Event.date.asc()).all()
    return jsonify([event.to_dict() for event in events])

@bp.route('/past', methods=['GET'])
def get_past_events():
    today = get_today()
    events = Event.query.filter(Event.date < today).order_by(Event.date.desc()).all()
    return jsonify([event.to_dict() for event in events])

@bp.route('', methods=['POST'])
def create_event():
    if not check_auth():
        return jsonify({'error': 'unauthorized'}), 401
    
    try:
        from flask import current_app
        
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        location = request.form.get('location')
        category = request.form.get('category')
        
        if not title or not date_str:
            return jsonify({'error': 'title and date are required'}), 400
        
        event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        event_time = datetime.strptime(time_str, '%H:%M').time() if time_str else None
        
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                image_path = save_upload(file, current_app)
        
        event = Event(
            title=title,
            description=description,
            image_path=image_path,
            date=event_date,
            time=event_time,
            location=location,
            category=category
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify(event.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:id>', methods=['PUT'])
def update_event(id):
    if not check_auth():
        return jsonify({'error': 'unauthorized'}), 401
    
    event = Event.query.get_or_404(id)
    
    try:
        from flask import current_app
        
        if request.is_json:
            data = request.get_json()
            event.title = data.get('title', event.title)
            event.description = data.get('description', event.description)
            event.location = data.get('location', event.location)
            event.category = data.get('category', event.category)
            
            if 'date' in data:
                event.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            if 'time' in data:
                event.time = datetime.strptime(data['time'], '%H:%M').time() if data['time'] else None
        else:
            event.title = request.form.get('title', event.title)
            event.description = request.form.get('description', event.description)
            event.location = request.form.get('location', event.location)
            event.category = request.form.get('category', event.category)
            
            if request.form.get('date'):
                event.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
            if request.form.get('time'):
                event.time = datetime.strptime(request.form.get('time'), '%H:%M').time()
            
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    if event.image_path:
                        old_path = os.path.join(current_app.root_path, event.image_path.lstrip('/'))
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    event.image_path = save_upload(file, current_app)
        
        event.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(event.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:id>', methods=['DELETE'])
def delete_event(id):
    if not check_auth():
        return jsonify({'error': 'unauthorized'}), 401
    
    event = Event.query.get_or_404(id)
    
    try:
        from flask import current_app
        
        if event.image_path:
            file_path = os.path.join(current_app.root_path, event.image_path.lstrip('/'))
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.session.delete(event)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/pdf', methods=['GET'])
def generate_pdf():
    from utils.pdf_generator import generate_events_pdf
    
    try:
        pdf_path = generate_events_pdf()
        return send_file(pdf_path, mimetype='application/pdf', as_attachment=True, download_name='events_calendar.pdf')
    except Exception as e:
        return jsonify({'error': str(e)}), 500
