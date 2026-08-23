from datetime import date
from app import create_app
from config.database import db
from models.holiday import Holiday

INDIAN_HOLIDAYS_2026 = [
    ('New Year''s Day',          date(2026, 1,  1),  'Public Holiday'),
    ('Makar Sankranti',          date(2026, 1, 14),  'Harvest festival'),
    ('Republic Day',             date(2026, 1, 26),  'National Holiday'),
    ('Maha Shivratri',           date(2026, 2, 17),  'Hindu festival'),
    ('Holi',                     date(2026, 3, 20),  'Festival of colours'),
    ('Ram Navami',               date(2026, 3, 29),  'Hindu festival'),
    ('Eid ul-Fitr',              date(2026, 3, 31),  'Muslim festival (approx.)'),
    ('Good Friday',              date(2026, 4,  3),  'Christian holiday'),
    ('Dr. Ambedkar Jayanti',     date(2026, 4, 14),  'National Holiday'),
    ('Akshaya Tritiya',          date(2026, 4, 20),  'Hindu auspicious day'),
    ('Buddha Purnima',           date(2026, 5,  3),  'Buddhist festival'),
    ('Eid ul-Adha',              date(2026, 6,  7),  'Muslim festival (approx.)'),
    ('Muharram',                 date(2026, 7,  6),  'Islamic New Year (approx.)'),
    ('Independence Day',         date(2026, 8, 15),  'National Holiday'),
    ('Ganesh Chaturthi',         date(2026, 8, 25),  'Hindu festival'),
    ('Onam',                     date(2026, 9,  3),  'Harvest festival (Kerala)'),
    ('Gandhi Jayanti',           date(2026, 10, 2),  'National Holiday'),
    ('Navratri Start',           date(2026, 10, 3),  'Hindu festival'),
    ('Dussehra / Vijayadashami', date(2026, 10,12),  'Hindu festival'),
    ('Milad-un-Nabi',            date(2026, 10,15),  'Prophet Birthday (approx.)'),
    ('Diwali',                   date(2026, 10,30),  'Festival of Lights'),
    ('Govardhan Puja',           date(2026, 10,31),  'Hindu festival'),
    ('Bhai Dooj',                date(2026, 11, 1),  'Hindu festival'),
    ('Guru Nanak Jayanti',       date(2026, 11,14),  'Sikh festival'),
    ('Christmas Day',            date(2026, 12,25),  'Christian holiday'),
]

app = create_app()
with app.app_context():
    added = 0
    skipped = 0
    for name, hdate, desc in INDIAN_HOLIDAYS_2026:
        existing = Holiday.query.filter_by(date=hdate).first()
        if existing:
            print(f'  SKIP  {hdate}  {name} (already exists)')
            skipped += 1
        else:
            h = Holiday(name=name, date=hdate, description=desc)
            db.session.add(h)
            print(f'  ADD   {hdate}  {name}')
            added += 1
    db.session.commit()
    print(f'\nDone -- {added} holidays added, {skipped} skipped.')
