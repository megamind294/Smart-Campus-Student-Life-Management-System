"""Run LAB 2 against real local PostgreSQL, MongoDB and MinIO services.

All generated images and prediction documents are synthetic test fixtures.
Only the dedicated lab table/collection/object keys are replaced on a rerun.
"""
from pathlib import Path
import sys, json, hashlib, time, io
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'packages'))
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from pymongo import MongoClient, DESCENDING
from minio import Minio
from PIL import Image, ImageDraw

EVIDENCE = ROOT / 'evidence'
IMAGES = ROOT / 'test_images'
EVIDENCE.mkdir(exist_ok=True)
IMAGES.mkdir(exist_ok=True)
PASSWORD = 'lab2-local-demo-2026'  # disposable local laboratory credentials
BUCKET = 'ai-images'

def default(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)

def save(name, value):
    (EVIDENCE / name).write_text(json.dumps(value, indent=2, default=default), encoding='utf-8')

def connect():
    deadline = time.monotonic() + 180
    last = None
    while time.monotonic() < deadline:
        try:
            pg = psycopg2.connect(host='127.0.0.1', port=55432, dbname='ailab', user='labuser', password=PASSWORD, connect_timeout=3)
            mongo = MongoClient('mongodb://labuser:' + PASSWORD + '@127.0.0.1:57017/?authSource=admin', serverSelectionTimeoutMS=3000, tz_aware=True)
            mongo.admin.command('ping')
            obj = Minio('127.0.0.1:59000', access_key='lab2minio', secret_key=PASSWORD, secure=False)
            obj.list_buckets()
            return pg, mongo, obj
        except Exception as exc:
            last = exc
            time.sleep(2)
    raise RuntimeError(f'Laboratory services unavailable: {last}')

pg, mongo, obj = connect()
pg.autocommit = True
col = mongo.ailab.prediction_logs
DDL = '''CREATE TABLE IF NOT EXISTS images (
    image_id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    width INTEGER NOT NULL CHECK (width > 0),
    height INTEGER NOT NULL CHECK (height > 0),
    source TEXT NOT NULL,
    storage_path TEXT NOT NULL UNIQUE,
    upload_date TIMESTAMPTZ NOT NULL
);'''
(ROOT / 'schema.sql').write_text(DDL + '\n', encoding='utf-8')
with pg.cursor() as cur:
    cur.execute(DDL)
    cur.execute('CREATE INDEX IF NOT EXISTS images_category_idx ON images(category)')
    cur.execute('CREATE INDEX IF NOT EXISTS images_source_idx ON images(source)')
    cur.execute('CREATE INDEX IF NOT EXISTS images_upload_date_idx ON images(upload_date)')

if not obj.bucket_exists(BUCKET):
    obj.make_bucket(BUCKET)
records, docs, hashes = [], [], {}
categories = ['building', 'classroom', 'sign', 'bicycle']
colors = ['#d9eaf7', '#e8ecd5', '#f7dfc2', '#e7dafa']
for i in range(1, 21):
    image_id = 100 + i
    category = categories[(i - 1) % 4]
    filename = f'campus_{image_id}.png'
    width, height = 320 + i * 4, 240 + i * 3
    im = Image.new('RGB', (width, height), colors[(i - 1) % 4])
    draw = ImageDraw.Draw(im)
    draw.rectangle((20, 35, width - 20, height - 40), outline='#203849', width=4)
    draw.text((30, 15), f'SYNTHETIC CAMPUS TEST IMAGE {image_id}', fill='#203849')
    draw.text((30, height - 28), category, fill='#203849')
    draw.ellipse((50, 70, 110, 130), outline='#203849', width=3)
    file = IMAGES / filename
    im.save(file)
    hashes[image_id] = hashlib.sha256(file.read_bytes()).hexdigest()
    timestamp = datetime(2026, 10, 20, 10, tzinfo=timezone.utc) + timedelta(hours=i - 1)
    source = 'campus-demo-a' if i % 2 else 'campus-demo-b'
    obj.fput_object(BUCKET, filename, str(file), content_type='image/png', metadata={'image-id': str(image_id), 'synthetic': 'true'})
    records.append((image_id, filename, category, width, height, source, BUCKET + '/' + filename, timestamp))
    doc = {'_id': f'lab2-prediction-{image_id}', 'image_id': image_id, 'model_version': 'v3' if i % 2 else 'v4',
           'prediction': category, 'confidence': round(0.72 + (i % 10) * 0.03, 2),
           'processing_time_ms': 30 + i * 2, 'device': 'GPU' if i % 2 == 0 else 'CPU',
           'timestamp': timestamp, 'synthetic': True}
    if i % 3 == 0:
        doc.update(temperature=60 + i, augmentation='flip')
    if i % 4 == 0:
        doc['explanation'] = {'method': 'fixture', 'region_count': i // 4}
    docs.append(doc)

with pg.cursor() as cur:
    execute_values(cur, '''INSERT INTO images VALUES %s ON CONFLICT (image_id)
    DO UPDATE SET filename=EXCLUDED.filename, category=EXCLUDED.category,
    width=EXCLUDED.width, height=EXCLUDED.height, source=EXCLUDED.source,
    storage_path=EXCLUDED.storage_path, upload_date=EXCLUDED.upload_date''', records)
for doc in docs:
    col.replace_one({'_id': doc['_id']}, doc, upsert=True)
col.create_index([('image_id', 1), ('timestamp', -1)])
col.create_index('model_version')
col.create_index([('confidence', -1), ('image_id', 1)])

sql_queries = {
    '6_all_images': 'SELECT * FROM images ORDER BY image_id;',
    '7_category': "SELECT * FROM images WHERE category = 'building' ORDER BY image_id;",
    '8_counts': 'SELECT category, COUNT(*) AS image_count FROM images GROUP BY category ORDER BY category;',
    '9_source': "SELECT * FROM images WHERE source = 'campus-demo-a' ORDER BY image_id;",
    '10_upload_order': 'SELECT * FROM images ORDER BY upload_date DESC, image_id;'
}
sql_results = {}
with pg.cursor(cursor_factory=RealDictCursor) as cur:
    for key, query in sql_queries.items():
        cur.execute(query)
        sql_results[key] = {'query': query, 'rows': [dict(r) for r in cur.fetchall()]}
save('postgres-results.json', sql_results)
save('mongo-seed-documents.json', docs)
mongo_results = {
    '11_model_v3': {'query': "db.prediction_logs.find({model_version: 'v3'}).sort({image_id: 1})", 'documents': list(col.find({'model_version': 'v3'}).sort('image_id', 1))},
    '12_confidence': {'query': 'db.prediction_logs.find({confidence: {$gt: 0.9}}).sort({image_id: 1})', 'documents': list(col.find({'confidence': {'$gt': 0.9}}).sort('image_id', 1))},
    '13_classes': {'query': "db.prediction_logs.aggregate([{$group: {_id: '$prediction', count: {$sum: 1}}}, {$sort: {_id: 1}}])", 'documents': list(col.aggregate([{'$group': {'_id': '$prediction', 'count': {'$sum': 1}}}, {'$sort': {'_id': 1}}]))},
    '14_optional': {'query': 'db.prediction_logs.find({temperature: {$exists: true}}).sort({image_id: 1})', 'documents': list(col.find({'temperature': {'$exists': True}}).sort('image_id', 1))},
    '15_highest': {'query': 'db.prediction_logs.find().sort({confidence: -1, image_id: 1}).limit(1)', 'documents': list(col.find().sort([('confidence', DESCENDING), ('image_id', 1)]).limit(1))}
}
save('mongo-results.json', mongo_results)
objects = []
for item in obj.list_objects(BUCKET, recursive=True):
    if item.object_name.startswith('campus_'):
        objects.append({'bucket': BUCKET, 'key': item.object_name, 'size_bytes': item.size, 'etag': item.etag})
save('minio-objects.json', objects)

# Task 7: fetch metadata and newest log, then verify the referenced object.
selected_id = 105
with pg.cursor(cursor_factory=RealDictCursor) as cur:
    cur.execute('SELECT * FROM images WHERE image_id = %s', (selected_id,))
    metadata = dict(cur.fetchone())
prediction = col.find_one({'image_id': selected_id}, sort=[('timestamp', DESCENDING)])
bucket, key = metadata['storage_path'].split('/', 1)
stat = obj.stat_object(bucket, key)
response = obj.get_object(bucket, key)
try:
    downloaded = response.read()
finally:
    response.close()
    response.release_conn()
combined = {'image_id': selected_id, 'postgresql': metadata, 'mongodb': prediction,
            'minio': {'bucket': bucket, 'key': key, 'storage_path': bucket + '/' + key,
                      'size_bytes': stat.size, 'content_type': stat.content_type,
                      'sha256': hashlib.sha256(downloaded).hexdigest(),
                      'sha256_matches_original': hashlib.sha256(downloaded).hexdigest() == hashes[selected_id]}}
save('combined-result.json', combined)

pg_ids = {r['image_id'] for r in sql_results['6_all_images']['rows']}
mongo_ids = {r['image_id'] for r in col.find({}, {'image_id': 1})}
object_ids = {int(o['key'].split('_')[1].split('.')[0]) for o in objects}
checks = {
    'postgres_exactly_20_records': len(pg_ids) == 20,
    'mongo_exactly_20_documents': col.count_documents({}) == 20,
    'minio_exactly_20_images': len(objects) == 20,
    'all_three_id_sets_equal': pg_ids == mongo_ids == object_ids,
    'four_categories_each_five': all(r['image_count'] == 5 for r in sql_results['8_counts']['rows']),
    'strict_confidence_filter': all(r['confidence'] > .9 for r in mongo_results['12_confidence']['documents']),
    'optional_temperature_varies': 0 < len(mongo_results['14_optional']['documents']) < 20,
    'selected_object_hash_matches': combined['minio']['sha256_matches_original'],
    'selected_image_dimensions_match_metadata': Image.open(io.BytesIO(downloaded)).size == (metadata['width'], metadata['height'])
}
with pg.cursor() as cur:
    cur.execute('SELECT version()')
    pg_version = cur.fetchone()[0]
save('verification.json', {'checks': checks, 'all_passed': all(checks.values()),
      'postgres_version': pg_version, 'mongodb_version': mongo.server_info()['version'],
      'actual_run_utc': datetime.now(timezone.utc), 'fixture_timestamps': '2026-10-20 and 2026-10-21 UTC; synthetic, not execution times',
      'scope': 'Generated fixtures and database/storage operations; no AI model inference performed.'})
print(json.dumps({'checks': checks, 'all_passed': all(checks.values()), 'selected_image': combined}, indent=2, default=default))
mongo.close()
pg.close()
assert all(checks.values()), checks
