"""Render the report only from recorded laboratory results."""
from pathlib import Path
import json, textwrap, html, zipfile, os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parent
OUT=Path(os.environ.get('LAB2_OUTPUT_DIR', str(ROOT.parent.parent/'outputs')))
E=ROOT/'evidence'
def read(name):return json.loads((E/name).read_text(encoding='utf-8-sig'))
sql=read('postgres-results.json');mongo=read('mongo-results.json');objects=read('minio-objects.json');combined=read('combined-result.json');verification=read('verification.json')
assert verification['all_passed'], 'Cannot produce a completed report with failed checks'
OUT.mkdir(exist_ok=True)
fonts=Path('C:/Windows/Fonts')
normal=fonts/'arial.ttf'
bold=fonts/'arialbd.ttf'
if not normal.exists():
    normal=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    bold=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
pdfmetrics.registerFont(TTFont('Body',str(normal)))
pdfmetrics.registerFont(TTFont('BodyBold',str(bold)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Body2',fontName='Body',fontSize=9.3,leading=13,spaceAfter=7,textColor=colors.HexColor('#25384A')))
styles.add(ParagraphStyle(name='Title2',fontName='BodyBold',fontSize=27,leading=32,textColor=colors.HexColor('#123E57'),spaceAfter=16))
styles.add(ParagraphStyle(name='Head2',fontName='BodyBold',fontSize=18,leading=23,textColor=colors.HexColor('#123E57'),spaceAfter=12))
styles.add(ParagraphStyle(name='Sub2',fontName='BodyBold',fontSize=11,leading=15,textColor=colors.HexColor('#137E88'),spaceBefore=6,spaceAfter=7))
styles.add(ParagraphStyle(name='Small2',fontName='Body',fontSize=7.8,leading=10.5,spaceAfter=5,textColor=colors.HexColor('#43586A')))
styles.add(ParagraphStyle(name='Code2',fontName='Courier',fontSize=7.1,leading=9.1,spaceBefore=4,spaceAfter=9,backColor=colors.HexColor('#F0F4F7'),borderPadding=7))
story=[]
def p(t,sty='Body2'):story.append(Paragraph(t,styles[sty]))
def h(t):p(t,'Sub2')
def title(t):p(t,'Head2')
def page():story.append(PageBreak())
def code(t,width=93):
    lines=[]
    for line in t.strip('\n').splitlines():
        lines.extend(textwrap.wrap(line,width=width,replace_whitespace=False,drop_whitespace=False) or [''])
    story.append(Preformatted('\n'.join(lines),styles['Code2']))
def table(headers,rows,widths,small=False):
    sty='Small2' if small else 'Body2'
    data=[[Paragraph(html.escape(str(c)),styles['Small2']) for c in headers]]
    data += [[Paragraph(html.escape(str(c)),styles[sty]) for c in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    pad=4 if small else 6
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E0EDF2')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),pad),('BOTTOMPADDING',(0,0),(-1,-1),pad),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#84ADB9')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F6F8FA')]),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#D8E2E8'))]))
    story.append(t);story.append(Spacer(1,8))
def ids(rows):return ', '.join(str(r['image_id']) for r in rows)
def footer(c,d):
    c.setStrokeColor(colors.HexColor('#BCD0D9'));c.line(43,45,552,45)
    c.setFont('Body',7.5);c.setFillColor(colors.HexColor('#4C6473'))
    c.drawString(43,31,'LAB 2  |  Data Storage Methods in AI Systems')
    c.drawRightString(552,31,str(d.page))

p('LABORATORY REPORT','Sub2')
p('SQL + NoSQL +<br/>Object Storage','Title2')
p('LAB 2 - Data Storage Methods in AI Systems','Sub2')
p('Smart Campus image-storage prototype','Body2')
story.append(Spacer(1,17))
table(['Group member','Student ID'],[['Rinkle Sharma','67784'],['Saisri Akkireddi','66918']],[365,144])
p('Report date: 30 October 2026. One report for the group; one group member submits it.','Small2')
h('Objective and scope')
p('This laboratory combines PostgreSQL for structured image metadata, MongoDB for flexible prediction-log documents, and MinIO for image files. A common image_id and a stored bucket/object key connect the three systems.')
p('The exercise uses a Smart Campus context: building, classroom, sign and bicycle images. The source React Smart Campus application is background context only. This is a separate storage prototype; the existing application was not integrated with these services.')
h('What was actually executed')
table(['Storage / check','Recorded result'],[['PostgreSQL','20 image metadata records; all five required SQL queries executed.'],['MongoDB','20 synthetic prediction documents; all five required operations executed.'],['MinIO','20 generated PNG images uploaded; corresponding metadata verified.'],['Cross-system retrieval','image_id 105 retrieved; downloaded file hash and dimensions checked.'],['Verification',f"{sum(verification['checks'].values())}/{len(verification['checks'])} recorded consistency checks passed."]],[140,369])
p('Evidence boundary: images and prediction logs are deliberately synthetic fixtures. No trained AI model was run, and confidence values are not measured model performance. Fixture timestamps are sample data; actual execution time is recorded separately. Production capacity and architecture are design analysis, not a 2-million-image benchmark.','Small2')

page();title('Task 1. Decide where data should be stored')
p('Storage is chosen by structure, size, access patterns, schema flexibility and query needs. The following decisions cover every data type listed in the instruction.')
table(['Data type','Storage','Decision and justification'],[
['Users','PostgreSQL','Small, stable records read at login and updated relatively infrequently. Unique identities, relations, authorization and transactional updates fit relational constraints. Store password hashes, never plaintext passwords.'],
['Image metadata','PostgreSQL','Small structured rows, frequently filtered by category, source, owner or date. Indexes, joins and constraints support consistent search and object references.'],
['Images','MinIO','Large binary objects, written at upload and read by inference or download. Bucket/key access and independent capacity scaling suit files better than embedding bytes in metadata rows.'],
['Model predictions','MongoDB + PostgreSQL references','High-volume per-inference documents vary by model (class, boxes, confidence, timings). Keep detailed payloads in MongoDB; image_id and a model-version reference connect them to the metadata/model registry.'],
['AI logs','MongoDB','Append-heavy, potentially millions of varied documents. Index image/model/time for investigations; use retention policies for disposable operational events. Avoid indexing every field.'],
['Experiment configurations','MongoDB','Nested hyperparameters, transforms and evaluation summaries change between experiments. Documents retain each configuration snapshot; experiment_id links the run to model registry entries.'],
['Model versions','PostgreSQL + MinIO','Small structured registry records need unique versions and reproducible provenance. Large weight/checkpoint files belong in MinIO; registry rows retain object keys and checksums.'],
['Error messages','MongoDB','Append-heavy diagnostics have optional stacks, devices and request context. Query by severity, component, time and correlation ID; redact sensitive input and set retention.']
],[91,107,311],small=True)
h('Why not put everything in one database?')
p('Binary files, relational identities and changing log payloads have different access and lifecycle needs. One store can handle several of these, but forcing every workload into it can increase backup size, query contention and schema complexity. Separate stores allow independent tuning and scaling. The tradeoff is extra operational work and application-level consistency between systems.')

page();title('Task 2. Architecture case - 2 million images')
h('1. Storage calculation')
code('2,000,000 images x 5 MB/image = 10,000,000 MB\nUsing decimal units (1 MB = 10^6 bytes):\n10,000,000 x 10^6 = 10^13 bytes = 10 TB\n10^13 / 2^40 = approximately 9.095 TiB')
p('The question uses MB, so the primary answer is approximately <b>10 TB of raw image payload</b>. If 5 MiB were intended instead, the total would be about 9.537 TiB (10.486 TB). These conventions must not be mixed.')
p('Raw payload excludes metadata, prediction logs, filesystem/object overhead, versions, replication or erasure coding, backups and growth. For illustration, three complete payload copies would require about 30 TB before other overhead. This is an example, not a recommendation or a measured cluster size.')
h('2-4. Storage decision and relational-database problems')
p('Store the images as MinIO objects, rather than embedding all files inside PostgreSQL rows. PostgreSQL can store binary data, but approximately 10 TB of images would substantially enlarge database backups and restores. Binary traffic can compete with metadata queries for I/O, cache and maintenance resources. Object storage lets the file workload grow separately and lets workers download files directly.')
h('5. Information retained in PostgreSQL')
p('Keep image_id, filename, category, width, height, source, upload_date and storage_path. A production design can also include user_id, size_bytes, content_type, checksum, upload_status and a model-version reference where appropriate. The implemented table contains the eight fields required by Task 4.')
code('PostgreSQL images row:\n  image_id:     105\n  filename:     campus_105.png\n  storage_path: ai-images/campus_105.png\n\nMinIO:\n  bucket: ai-images\n  key:    campus_105.png\n\nMongoDB prediction_logs:\n  image_id: 105  -> the same image identity')
p('Use a stable bucket/object key, rather than an expiring presigned URL, as the durable reference. URLs can be generated when an authorized client needs access. A production object key may include the immutable image_id and version to avoid accidental overwrites.')

page();title('Task 3. Start the storage environment')
p('The following docker-compose.yml starts three separate services. Ports bind to 127.0.0.1 and use distinct host ports. Named volumes keep laboratory data between container restarts. Credentials below are disposable local demo values.')
compose=(ROOT/'docker-compose.yml').read_text(encoding='utf-8')
code(compose,width=95)
p('The image tags above describe the run configuration. Exact pulled image identities and service versions are retained in the evidence archive so a mutable tag does not become the sole record of the environment.','Small2')

page();title('Task 3. Build the MinIO container')
p('The prebuilt MinIO image could not be pulled. This Dockerfile builds the official community source release in a Go compiler container and copies its binary into a separate runtime image. Docker Compose builds it before starting the MinIO service.')
code((ROOT/'Dockerfile.minio').read_text(encoding='utf-8'))
p('The source release is fixed, and the actual source commit is recorded by git rev-parse HEAD. The build does not replace MinIO with an S3 emulator. This is an isolated teaching deployment; the production architecture in Task 8 is a design proposal.')
p('Source/build reference: <link href="https://github.com/minio/minio/tree/RELEASE.2025-09-07T16-13-09Z" color="#137E88">official MinIO source release</link>.','Small2')

page();title('Task 3. Running services and availability')
code('docker compose -f docker-compose.yml up --build -d\ndocker compose -f docker-compose.yml ps\npython run_lab.py')
status=(E/'compose-ps.txt').read_text(encoding='utf-8-sig')
code(status,width=95)
table(['Service','Host endpoint','Purpose'],[['PostgreSQL','127.0.0.1:55432','ailab database; constrained image metadata and indexed lookups.'],['MongoDB','127.0.0.1:57017','ailab.prediction_logs; flexible model-output documents.'],['MinIO API','127.0.0.1:59000','ai-images bucket; original image bytes.'],['MinIO Console','127.0.0.1:59001','Optional web interface; the run used the Python client.']],[100,145,264])
h('Availability verification')
p('The execution script successfully established a PostgreSQL connection, sent a MongoDB ping and listed MinIO buckets before loading data. It then executed real reads and writes in all three systems. A running-container status alone is not treated as proof that the exercise succeeded.')
table(['Recorded version / time','Value'],[['PostgreSQL',verification['postgres_version']],['MongoDB',verification['mongodb_version']],['Actual execution (UTC)',verification['actual_run_utc']]],[150,359],small=True)
p('The UTC execution timestamp is distinct from the fixture upload_date and log timestamps. The latter deliberately start on 20 October 2026 to give deterministic sorting results.','Small2')
p('MinIO is compiled from its official source release RELEASE.2025-09-07T16-13-09Z using the companion Dockerfile.minio. The source commit and binary version are captured in the evidence archive. The unavailable prebuilt image was not substituted with a different storage product.','Small2')

page();title('Task 4. Structured metadata in PostgreSQL')
h('Table definition and indexes')
code((ROOT/'schema.sql').read_text(encoding='utf-8')+'\nCREATE INDEX images_category_idx ON images(category);\nCREATE INDEX images_source_idx ON images(source);\nCREATE INDEX images_upload_date_idx ON images(upload_date);')
p('INTEGER identifies each image and stores its pixel dimensions. TEXT holds filenames, labels and object references. TIMESTAMPTZ preserves an unambiguous upload instant. Primary and unique keys prevent duplicate identities and file references; CHECK constraints reject non-positive dimensions.')
h('Twenty inserted records - compact result of query 6')
table(['ID','Filename','Category','Pixels','Source'],[[r['image_id'],r['filename'],r['category'],f"{r['width']} x {r['height']}",r['source']] for r in sql['6_all_images']['rows']],[35,119,91,87,177],small=True)
p('For every row, storage_path is ai-images/&lt;filename&gt;. upload_date begins at 2026-10-20 10:00:00+00:00 for image 101 and increases one hour per image. Complete eight-column results are retained in postgres-results.json.','Small2')

page();title('Task 4. SQL queries and actual results')
for key,label in [('6_all_images','6. Display all images'),('7_category','7. Find images in the selected category'),('8_counts','8. Count images in each category'),('9_source','9. Find images from the selected source'),('10_upload_order','10. Sort images by upload date')]:
    h(label);q=sql[key];code(q['query'])
    if key=='8_counts':table(['Category','Count'],[[r['category'],r['image_count']] for r in q['rows']],[300,209],small=True)
    else:p(f"Result: {len(q['rows'])} rows. image_id order: {ids(q['rows'])}.")
p('The date-sorted result runs from image 120 (2026-10-21 05:00 UTC) back to image 101 (2026-10-20 10:00 UTC). These are seeded upload times, not the actual execution time.')
h('Why PostgreSQL fits this data')
p('Metadata has a consistent schema, small records and predictable filters. SQL grouping, sorting and indexing answer the required searches directly. Constraints validate identity and dimensions. In production, users and model versions can be linked through foreign keys, while the storage_path remains a logical external reference to MinIO.')

page();title('Task 5. Flexible documents in MongoDB')
p('The collection is <b>ailab.prediction_logs</b>. Twenty synthetic documents were inserted using replace_one(..., upsert=True) with deterministic _id values, so rerunning this dedicated fixture does not duplicate its logs. All contain image_id; optional fields intentionally vary.')
h('Example document with the base structure')
doc1=read('mongo-seed-documents.json')[0]
code(json.dumps(doc1,indent=2))
h('Example document with optional fields')
doc2=next(d for d in read('mongo-seed-documents.json') if 'temperature' in d and 'explanation' in d)
code(json.dumps(doc2,indent=2))
p('The generator uses confidence = round(0.72 + (i % 10) * 0.03, 2), alternating model versions and four rotating class labels. temperature and augmentation appear every third record; explanation appears every fourth. These values are test fixtures, not measurements from a GPU or classifier.','Small2')

page();title('Task 5. Queries and actual results')
for key,label in [('11_model_v3','11. Logs for model version v3'),('12_confidence','12. Confidence strictly greater than 0.9'),('13_classes','13. Prediction count for each class'),('14_optional','14. Documents containing temperature'),('15_highest','15. Highest-confidence prediction')]:
    h(label);v=mongo[key];code(v['query'])
    if key=='13_classes':table(['Prediction class','Count'],[[r['_id'],r['count']] for r in v['documents']],[300,209],small=True)
    elif key=='15_highest':
        r=v['documents'][0];p(f"Result: image_id {r['image_id']}, prediction {r['prediction']}, model {r['model_version']}, confidence {r['confidence']}. The ascending image_id tie-break selects a deterministic record when multiple documents share the highest confidence.")
    else:p(f"Result: {len(v['documents'])} documents. image_id values: {ids(v['documents'])}.")
h('Why a document model is convenient here')
p('Different model outputs can keep optional scalars, nested explanations and future fields in one collection without adding a relational column for every variant. Common fields remain queryable. This flexibility still needs validation, consistent identifiers and deliberate indexes; it does not mean that arbitrary incompatible documents are desirable. PostgreSQL JSONB would also be a valid alternative when relational joins and transactions dominate the workload.')

page();title('Task 6. Images in MinIO')
p('Bucket: <b>ai-images</b>. Twenty simple PNG test images were generated and uploaded using fput_object(..., content_type="image/png"). The object bytes reside in MinIO, while the corresponding PostgreSQL row keeps the key and descriptive metadata.')
table(['Object key in ai-images','Bytes','PostgreSQL image_id'],[[o['key'],o['size_bytes'],int(o['key'].split('_')[1].split('.')[0])] for o in objects],[280,100,129],small=True)
p('The table is an actual list_objects result, not an illustrative bucket listing. Complete object keys, sizes and ETags are saved in minio-objects.json. ETags are retained as returned by MinIO; SHA-256 is calculated separately for the cross-system integrity check.','Small2')
h('One corresponding metadata record')
r=combined['postgresql'];code(json.dumps(r,indent=2))
p('Split storage_path at its first slash: ai-images is the bucket and campus_105.png is the object key. A successful stat_object and get_object verify the referenced file exists. All 20 PostgreSQL IDs, MongoDB image IDs and object-derived IDs were compared and matched.')

page();title('Task 7. Connect the three storage systems')
h('Retrieval code - parameterized SQL and common image_id')
code('''selected_id = 105
with pg.cursor(cursor_factory=RealDictCursor) as cur:
    cur.execute("SELECT * FROM images WHERE image_id = %s", (selected_id,))
    metadata = dict(cur.fetchone())
prediction = col.find_one(
    {"image_id": selected_id}, sort=[("timestamp", DESCENDING)])
bucket, key = metadata["storage_path"].split("/", 1)
stat = obj.stat_object(bucket, key)
response = obj.get_object(bucket, key)
try:
    downloaded = response.read()
finally:
    response.close()
    response.release_conn()
sha256 = hashlib.sha256(downloaded).hexdigest()''')
h('Combined result - image 105')
table(['System','Retrieved values'],[['PostgreSQL',f"image_id={r['image_id']}; filename={r['filename']}; category={r['category']}; pixels={r['width']} x {r['height']}; source={r['source']}; upload_date={r['upload_date']}"],['MongoDB',f"image_id={combined['mongodb']['image_id']}; model_version={combined['mongodb']['model_version']}; prediction={combined['mongodb']['prediction']}; confidence={combined['mongodb']['confidence']}; synthetic=true"],['MinIO',f"{combined['minio']['storage_path']}; {combined['minio']['size_bytes']} bytes; {combined['minio']['content_type']}"],['Integrity',f"SHA-256 matches generated original: {combined['minio']['sha256_matches_original']}"]],[100,409])
code('SHA-256: '+combined['minio']['sha256'])
story.append(RLImage(str(ROOT/'test_images'/'campus_105.png'),width=204,height=153))
p('Retrieved fixture shown above; it is a generated test graphic. The full combined record is in combined-result.json. image_id provides identity across PostgreSQL and MongoDB; PostgreSQL storage_path locates the MinIO bytes. No cross-database foreign-key constraint or atomic transaction is implied.','Small2')

page();title('Task 8. Production storage architecture')
p('Design target: 2,000,000 images, 10,000 users, multiple model versions, millions of prediction logs and experiment history. The diagram is a proposed production design; only the three storage services and the laboratory operations were executed.')
# Vector architecture diagram, kept inside the page and independent of raster generation.
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
d=Drawing(509,230)
def box(x,y,w,h,label,sub):
    d.add(Rect(x,y,w,h,rx=6,fillColor=colors.HexColor('#E7F0F4'),strokeColor=colors.HexColor('#6A9CAF')))
    d.add(String(x+10,y+h-20,label,fontName='BodyBold',fontSize=10,fillColor=colors.HexColor('#123E57')))
    d.add(String(x+10,y+13,sub,fontName='Body',fontSize=7.7,fillColor=colors.HexColor('#25384A')))
def arrow(x1,y1,x2,y2):
    d.add(Line(x1,y1,x2,y2,strokeColor=colors.HexColor('#137E88'),strokeWidth=1.5))
    d.add(Polygon([x2,y2,x2-7,y2+3,x2-7,y2-3],fillColor=colors.HexColor('#137E88'),strokeColor=None))
box(0,160,140,55,'Students / clients','Login, upload, search, retrieve')
box(180,160,150,55,'API + ingestion service','Auth, IDs, validation, outbox')
arrow(140,187,180,187)
box(0,65,150,65,'PostgreSQL','Users, metadata, model registry')
box(180,65,150,65,'MongoDB','Predictions, logs, experiments')
box(360,65,149,65,'MinIO','Images, weights, run artifacts')
for x in [75,255,434]:
    d.add(Line(255,160,255,144,strokeColor=colors.HexColor('#137E88')))
    d.add(Line(75,144,434,144,strokeColor=colors.HexColor('#137E88')))
    d.add(Line(x,144,x,130,strokeColor=colors.HexColor('#137E88')))
box(180,0,329,43,'Queue + inference / evaluation workers','Read objects and model versions; write correlated results')
story.append(d)
table(['Data','System','Production rationale'],[['Users / login','PostgreSQL','Unique user IDs, password hashes, roles and transactional account changes.'],['Images','MinIO','Original binaries, stable object keys, checksums and protected downloads.'],['Image metadata','PostgreSQL','Indexed owner/category/source/date filters and upload state.'],['Predictions and logs','MongoDB','Append-heavy model-specific documents, indexed by image/model/time; retention for disposable logs.'],['Experiment information','MongoDB + MinIO','Configuration and metric documents in MongoDB; large run artifacts in MinIO, linked by experiment_id.'],['Model information','PostgreSQL + MinIO','Unique version and provenance registry in PostgreSQL; checkpoints and weights in MinIO.']],[105,115,289],small=True)

page();title('Task 8. Operations, risks and solutions')
table(['Frequent operation','Storage path'],[['User login','API checks the PostgreSQL user record and verifies the password hash.'],['Image upload','API allocates image_id and pending metadata; uploads bytes to MinIO, verifies checksum, then marks metadata ready.'],['Image metadata search','PostgreSQL applies indexed filters and returns stable object references.'],['AI prediction / logging','Worker reads image and model objects from MinIO, then writes image_id/model-version-correlated output to MongoDB.'],['Model evaluation','Read version/experiment metadata and aggregate MongoDB results; store large evaluation artifacts in MinIO.'],['Retrieve original image','Authorize from PostgreSQL ownership/ready state, then fetch from MinIO or issue a short-lived URL.']],[130,379],small=True)
table(['Problem','Concrete scenario','Proposed solution'],[['Performance bottleneck','Workers repeatedly read 5 MB images through the API, saturating its network and increasing inference latency.','Let authorized workers read MinIO directly; cache hot objects near workers, batch metadata lookups and monitor bandwidth/latency.'],['Scalability problem','Prediction logs grow into millions of documents and large indexes; a single node cannot sustain writes and evaluation scans.','Retain only required logs, index actual query paths, separate analytics workloads and introduce measured sharding/partitioning when needed. Select a shard key from observed distribution, not model_version alone.'],['Failure scenario','Object upload succeeds but metadata finalization or log write fails, leaving an orphan object or incomplete result.','Use pending/ready/error states, deterministic idempotency keys, durable outbox/queue retries and a reconciliation job. Verify object existence/checksum before ready; alert on stale pending records.']],[87,184,238],small=True)
p('Back up and test restores for all stores, preserve identifier mappings and protect production endpoints with TLS, authentication and scoped permissions. The local one-node Compose setup demonstrates data placement; it is not a production availability or disaster-recovery deployment.')
h('Why combine SQL, NoSQL and object storage?')
p('The combination matches each workload to a useful data model: PostgreSQL supplies relational consistency and searchable metadata, MongoDB accommodates variable inference and experiment documents, and MinIO holds large binaries independently. It can reduce resource contention and enable separate scaling and retention. These gains depend on explicit ownership, common identifiers, retries and reconciliation; several stores do not automatically provide distributed atomicity.')

page();title('Verification and reproducibility')
table(['Executed consistency check','Result'],[[k.replace('_',' '),'PASS' if v else 'FAIL'] for k,v in verification['checks'].items()],[425,84],small=True)
h('Reproduce the laboratory')
code('''# In the extracted lab2 source directory:
python -m pip install psycopg2-binary pymongo minio pillow
docker compose up --build -d
docker compose ps
python run_lab.py
# Inspect evidence/*.json and the generated test_images/ directory.
# Stop the dedicated services when finished, preserving their volumes:
docker compose stop''')
p('The companion archive contains the exact Compose configuration, schema, execution script, generated images and raw results. The code uses real clients against loopback service ports. It does not substitute dictionaries or in-memory simulations for the required stores. No user-supplied database content was used as a fixture.')
h('Sources and evidence')
p('Primary assignment source: LAB_2.pdf supplied by the user, eight pages. Task and operation numbering in this report follows that document; its operations 6-18 remain inside Tasks 4-7. No Kanban, Agile essay or Scrum-assessment requirement is included because those belong to another course.','Small2')
p('Background project: <link href="https://github.com/megamind294/Smart-Campus-Student-Life-Management-System" color="#137E88">Smart Campus - Student Life Management System repository</link>. Only the campus context is reused; this report does not assert that the original frontend used PostgreSQL, MongoDB or MinIO.','Small2')
p('Execution evidence: compose-ps.txt; image-identities.json; postgres-results.json; mongo-seed-documents.json; mongo-results.json; minio-objects.json; combined-result.json; verification.json. These files are generated or captured from the actual laboratory run.','Small2')
p('Prepared with AI assistance for code, execution and report assembly. Synthetic fixtures and design proposals are explicitly distinguished from observed storage-operation results.','Small2')

pdf=OUT/'LAB_2_Rinkle_Sharma_Saisri_Akkireddi_Report.pdf'
doc=SimpleDocTemplate(str(pdf),pagesize=A4,rightMargin=43,leftMargin=43,topMargin=44,bottomMargin=59,title='LAB 2 - SQL + NoSQL + Object Storage',author='Rinkle Sharma; Saisri Akkireddi')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(pdf)
