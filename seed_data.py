from app import app, db
from models import Event, Sermon
from datetime import datetime, timedelta

def seed_database():
    with app.app_context():
        print("Clearing existing data...")
        Event.query.delete()
        Sermon.query.delete()
        db.session.commit()
        
        print("Creating sample events...")
        
        today = datetime.now().date()
        
        events_data = [
            {
                'title': 'Sunday Worship Service',
                'description': 'Join us for our weekly Sunday worship service. Experience uplifting music, powerful preaching, and fellowship with believers.',
                'date': today + timedelta(days=7),
                'time': datetime.strptime('10:00', '%H:%M').time(),
                'location': 'Main Sanctuary',
                'category': 'Service'
            },
            {
                'title': 'Youth Conference 2025',
                'description': 'An exciting three-day youth conference featuring worship, teaching, and activities designed for young people.',
                'date': today + timedelta(days=14),
                'time': datetime.strptime('18:00', '%H:%M').time(),
                'location': 'Conference Hall',
                'category': 'Conference'
            },
            {
                'title': 'Prayer and Fasting Week',
                'description': 'A week dedicated to seeking God through prayer and fasting. Daily prayer sessions at 6am and 6pm.',
                'date': today + timedelta(days=21),
                'time': datetime.strptime('06:00', '%H:%M').time(),
                'location': 'Prayer Room',
                'category': 'Prayer'
            },
            {
                'title': 'Community Outreach',
                'description': 'Join us as we reach out to our local community with food, clothing, and the love of Christ.',
                'date': today + timedelta(days=28),
                'time': datetime.strptime('09:00', '%H:%M').time(),
                'location': 'City Center',
                'category': 'Outreach'
            },
            {
                'title': 'Christmas Service',
                'description': 'Celebrate the birth of our Savior with us in a special Christmas worship service.',
                'date': today - timedelta(days=30),
                'time': datetime.strptime('19:00', '%H:%M').time(),
                'location': 'Main Sanctuary',
                'category': 'Service'
            },
            {
                'title': 'New Year Prayer Night',
                'description': 'We crossed over into the new year with prayer, worship, and thanksgiving.',
                'date': today - timedelta(days=60),
                'time': datetime.strptime('22:00', '%H:%M').time(),
                'location': 'Main Sanctuary',
                'category': 'Prayer'
            }
        ]
        
        for event_data in events_data:
            event = Event(**event_data)
            db.session.add(event)
        
        print("Creating sample sermons...")
        
        sermons_data = [
            {
                'title': 'The Power of Faith',
                'speaker_or_leader': 'Pastor John Kimani',
                'date': today - timedelta(days=7),
                'description': 'An inspiring message about walking by faith and not by sight, trusting God in all circumstances.',
                'media_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'title': 'Living a Purpose-Driven Life',
                'speaker_or_leader': 'Pastor Mary Wanjiru',
                'date': today - timedelta(days=14),
                'description': 'Discover God\'s purpose for your life and learn how to live with intentionality and meaning.',
                'media_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'title': 'The Joy of Salvation',
                'speaker_or_leader': 'Bishop David Mutua',
                'date': today - timedelta(days=21),
                'description': 'A powerful message about the joy that comes from knowing Christ and being saved by His grace.',
                'media_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'title': 'Building Strong Families',
                'speaker_or_leader': 'Pastor Grace Akinyi',
                'date': today - timedelta(days=28),
                'description': 'Practical wisdom on building Christ-centered families that honor God and thrive together.',
                'media_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'title': 'The Great Commission',
                'speaker_or_leader': 'Pastor John Kimani',
                'date': today - timedelta(days=35),
                'description': 'Understanding our call to go into all the world and preach the gospel to every creature.',
                'media_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            }
        ]
        
        for sermon_data in sermons_data:
            sermon = Sermon(**sermon_data)
            db.session.add(sermon)
        
        db.session.commit()
        print("Database seeded successfully!")
        print(f"Created {len(events_data)} events and {len(sermons_data)} sermons.")

if __name__ == '__main__':
    seed_database()
