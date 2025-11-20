from flask import Blueprint, request, jsonify
from models import db, Sermon
from datetime import datetime

bp = Blueprint('sermons', __name__, url_prefix='/api/sermons')

ADMIN_PASSWORD = 'Elim@2025'

def check_auth():
    password = request.headers.get('X-ADMIN-PASSWORD')
    if password != ADMIN_PASSWORD:
        return False
    return True

@bp.route('', methods=['GET'])
def get_all_sermons():
    sermons = Sermon.query.order_by(Sermon.date.desc()).all()
    return jsonify([sermon.to_dict() for sermon in sermons])

@bp.route('', methods=['POST'])
def create_sermon():
    if not check_auth():
        return jsonify({'error': 'unauthorized'}), 401
    
    try:
        data = request.get_json()
        
        title = data.get('title')
        speaker_or_leader = data.get('speaker_or_leader')
        date_str = data.get('date')
        description = data.get('description')
        media_url = data.get('media_url')
        
        if not title or not date_str:
            return jsonify({'error': 'title and date are required'}), 400
        
        sermon_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        sermon = Sermon(
            title=title,
            speaker_or_leader=speaker_or_leader,
            date=sermon_date,
            description=description,
            media_url=media_url
        )
        
        db.session.add(sermon)
        db.session.commit()
        
        return jsonify(sermon.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:id>', methods=['PUT'])
def update_sermon(id):
    if not check_auth():
        return jsonify({'error': 'unauthorized'}), 401
    
    sermon = Sermon.query.get_or_404(id)
    
    try:
        data = request.get_json()
        
        sermon.title = data.get('title', sermon.title)
        sermon.speaker_or_leader = data.get('speaker_or_leader', sermon.speaker_or_leader)
        sermon.description = data.get('description', sermon.description)
        sermon.media_url = data.get('media_url', sermon.media_url)
        
        if 'date' in data:
            sermon.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        sermon.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(sermon.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:id>', methods=['DELETE'])
def delete_sermon(id):
    if not check_auth():
        return jsonify({'error': 'unauthorized'}), 401
    
    sermon = Sermon.query.get_or_404(id)
    
    try:
        db.session.delete(sermon)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
