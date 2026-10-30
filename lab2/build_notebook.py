"""Create an honest, runnable notebook, attaching only observed outputs."""
from pathlib import Path
import json, ast, os
ROOT=Path(__file__).resolve().parent
OUT=Path(os.environ.get('LAB2_OUTPUT_DIR', str(ROOT.parent.parent/'outputs')));OUT.mkdir(exist_ok=True)
cells=[]
def md(s):cells.append({'cell_type':'markdown','metadata':{},'source':s.strip().splitlines(True)})
def code(s):
    ast.parse(s)
    cells.append({'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':s.strip().splitlines(True)})
done=(ROOT/'evidence'/'verification.json').exists()
status='Executed results are included below.' if done else '**Execution pending:** Docker Desktop could not start its WSL engine (`HCS_E_CONNECTION_TIMEOUT`). The code is prepared, but live database results have not been obtained. Run all cells with a working Docker engine before submission.'
md(f'''# LAB 2 - SQL + NoSQL + Object Storage
## Data Storage Methods in AI Systems

| Group member | Student ID |
|---|---|
| Rinkle Sharma | 67784 |
| Saisri Akkireddi | 66918 |

Report prepared: 30 October 2026. One report for the group; only one person submits it.

{status}

The Smart Campus setting is used for a separate image-storage prototype. The existing React application is not changed or integrated with these databases. All images and prediction documents are **synthetic test fixtures**; no trained model was run. The notebook follows Tasks 1-8 from the supplied LAB_2.pdf. Kanban and Scrum are not requirements of this laboratory.''')
md('''## Task 1. Decide where the data should be stored

| Data type | Storage | Justification: structure, size, access, flexibility and queries |
|---|---|---|
| Users | PostgreSQL | Small, stable relational records, frequent identity/permission lookups, uniqueness and transactional account updates. Store password hashes, not plaintext passwords. |
| Image metadata | PostgreSQL | Small structured rows; frequent category/source/owner/date filters, joins, constraints and indexed lookups. |
| Images | MinIO | Large binary objects written on upload and read for inference/download. Bucket/key access and separate capacity scaling suit the file workload. |
| Model predictions | MongoDB, linked to PostgreSQL IDs | Append-heavy model-specific payloads can contain labels, scores, boxes and nested optional results. Query by image_id/model/time. |
| AI logs | MongoDB | High-volume varying operational documents; index selected query fields and set retention for disposable logs. |
| Experiment configurations | MongoDB | Nested hyperparameters and transforms vary by experiment; keep immutable configuration snapshots keyed by experiment_id. Large artifacts go in MinIO. |
| Model versions | PostgreSQL + MinIO | Structured registry entries need unique versions and provenance. Large checkpoint/weight binaries belong in MinIO with keys/checksums in the registry. |
| Error messages | MongoDB | Append-heavy records have optional stacks and device/request context. Query severity/component/time; redact sensitive input. |

**Why not store everything in one database?** Binary files, relational identities and varying logs have different query and lifecycle needs. One store can support several workloads, but forcing every workload into it increases backup size, resource contention and schema complexity. Separate stores allow independent tuning, scaling and retention. The tradeoff is additional operations and application-level consistency; multiple stores do not provide automatic distributed atomicity.''')
md('''## Task 2. Architecture case - 2 million images

1. `2,000,000 x 5 MB = 10,000,000 MB = 10 TB` using decimal MB/TB (`10^13` bytes), approximately **9.095 TiB**. If the question instead meant 5 MiB, the total would be approximately 9.537 TiB (10.486 TB). These are different unit conventions.
2. Store the image bytes in MinIO, not directly in PostgreSQL for this design.
3. Ten TB of binary payload would enlarge database backups/restores and compete with metadata queries for I/O, cache and maintenance resources.
4. Store actual images as objects in MinIO. Capacity planning must also cover protection overhead, backups, versions, metadata, logs and growth. Three complete copies would be about 30 TB of image payload, as an illustration only.
5. PostgreSQL retains image_id, filename, category, width, height, source, storage_path and upload_date. Production extensions may include user_id, checksum, content_type, size_bytes and upload_status.

Example logical link:
```text
PostgreSQL: image_id=105, filename=campus_105.png,
            storage_path=ai-images/campus_105.png
MinIO:      bucket=ai-images, key=campus_105.png
MongoDB:    image_id=105, model_version=v3, ...
```
Store stable keys, not expiring presigned URLs. The external object reference is not enforced by a PostgreSQL foreign-key constraint.''')
code('''from pathlib import Path
import sys, subprocess, json, hashlib, io, time
from datetime import datetime, timedelta, timezone
ROOT = Path.cwd() / "lab2_execution"
ROOT.mkdir(exist_ok=True)
EVIDENCE = ROOT / "evidence"
EVIDENCE.mkdir(exist_ok=True)

# Install the real database clients in the current notebook's environment.
subprocess.run([sys.executable, "-m", "pip", "install", "psycopg2-binary", "pymongo", "minio", "pillow"], check=True)
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from pymongo import MongoClient, DESCENDING
from minio import Minio
from PIL import Image, ImageDraw

def show(value):
    print(json.dumps(value, indent=2, default=str))''')
md('''## Task 3. Start the storage environment with Docker Compose

PostgreSQL stores structured image metadata; MongoDB stores prediction logs; MinIO stores image bytes. The local services use independent named volumes and loopback host ports. The credentials below are disposable laboratory values. Run Docker Desktop first. These cells use real services and stop on failure rather than inventing outputs.''')
compose=(ROOT/'docker-compose.yml').read_text(encoding='utf-8')
dockerfile=(ROOT/'Dockerfile.minio').read_text(encoding='utf-8')
code('COMPOSE = '+repr(compose)+'\nDOCKERFILE = '+repr(dockerfile)+'''
compose_file = ROOT / "docker-compose.yml"
compose_file.write_text(COMPOSE, encoding="utf-8")
(ROOT / "Dockerfile.minio").write_text(DOCKERFILE, encoding="utf-8")
print(COMPOSE)
command = ["docker", "compose", "-f", str(compose_file)]
subprocess.run(command + ["up", "--build", "-d"], check=True)
status = subprocess.run(command + ["ps"], check=True, capture_output=True, text=True)
print(status.stdout)
(EVIDENCE / "compose-ps.txt").write_text(status.stdout, encoding="utf-8")
''')
script=(ROOT/'run_lab.py').read_text(encoding='utf-8')
# Include readable Python source rather than a one-line escaped script payload.
code(script.replace('ROOT = Path(__file__).resolve().parent', 'ROOT = Path.cwd() / "lab2_execution"')+'''

def evidence(name):
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))
''')
md('''## Task 4. Store structured metadata in PostgreSQL

The runner creates `images`, generates 20 test records (IDs 101-120), uploads corresponding image bytes, inserts metadata and executes operations 6-10. The next cell displays the table definition, complete SQL text and actual full query results. A primary key and unique references prevent duplicate identities; CHECK constraints validate positive dimensions. TIMESTAMPTZ gives unambiguous times. Fixture dates start at 20 October 2026; they are not execution timestamps.''')
code('''print((ROOT / "schema.sql").read_text())
for name, result in evidence("postgres-results.json").items():
    print("\\nOperation:", name)
    print(result["query"])
    show(result["rows"])
''')
md('''**Why PostgreSQL is suitable:** Metadata has a consistent schema, predictable filters and relational identity. SQL supports grouping and sorting directly; category/source/upload-date indexes help common searches. Users and model registry rows can later be connected through foreign keys, while file bytes remain in object storage.''')
md('''## Task 5. Store flexible documents in MongoDB

The collection is `ailab.prediction_logs`, with 20 deterministic synthetic documents. Each has image_id, model_version, prediction, confidence, processing_time_ms, device, timestamp and synthetic=true. Every third document adds temperature and augmentation; every fourth adds a nested explanation. No classifier or GPU measurement was performed. Operations 11-15 are executed against MongoDB and displayed below.''')
code('''documents = evidence("mongo-seed-documents.json")
show(documents[0])
show(next(d for d in documents if "temperature" in d and "explanation" in d))
for name, result in evidence("mongo-results.json").items():
    print("\\nOperation:", name)
    print(result["query"])
    show(result["documents"])
''')
md('''**Why MongoDB can be convenient:** Variable model outputs can retain optional scalars, nested explanations and future fields in the same collection without one relational column for every variant. Common identifiers and selected indexes still matter, and flexible documents still benefit from schema validation. PostgreSQL JSONB can also be appropriate when relational joins and transactions dominate.''')
md('''## Task 6. Store images in MinIO

Bucket: `ai-images`. The runner generates and uploads 20 PNG test images using `fput_object`, then records the real `list_objects` result. Every object has matching PostgreSQL metadata. Split storage_path at the first slash to obtain bucket and key. All three ID sets are compared; a selected object is statted, downloaded and checked by SHA-256 and dimensions.''')
code('''show(evidence("minio-objects.json"))
show(evidence("postgres-results.json")["6_all_images"]["rows"])
from IPython.display import display
display(Image.open(ROOT / "test_images" / "campus_105.png"))
''')
md('''## Task 7. Connect the storage systems

Use image_id=105 for operations 16-18. The SQL is parameterized. The newest MongoDB log is found by image_id; PostgreSQL storage_path identifies the MinIO bucket/key. The cell below shows the relevant retrieval fragment and the actual combined result. Logical identity does not imply an atomic cross-store transaction.''')
code('retrieval = '+repr(script.split('# Task 7:',1)[1].split('pg_ids =',1)[0])+'''
print(retrieval)
show(evidence("combined-result.json"))
show(evidence("verification.json"))
''')
md('''## Task 8. Architecture decision problem

The following is a proposed production design, not an executed 2-million-image load test.

```text
Students / clients
       |
 API + ingestion service -- queue/outbox --> inference / evaluation workers
       |                                           |
       +---- PostgreSQL: users, metadata, model registry
       +---- MongoDB: predictions, logs, experiment documents
       +---- MinIO: images, model weights, large run artifacts
```

| Element / operation | Storage choice and justification |
|---|---|
| Users and login | PostgreSQL for unique user identities, password hashes, roles and transactional changes. |
| Images / upload | MinIO for bytes; PostgreSQL for identity, owner, key, checksum and upload state. Allocate image_id, record pending metadata, upload/verify, then mark ready. |
| Metadata search | Indexed PostgreSQL filters by owner/category/source/date. |
| Model inference | Workers read images and versioned model binaries directly from MinIO and registry metadata from PostgreSQL. |
| Predictions and logging | MongoDB for model-specific output and append-heavy diagnostic documents linked through image_id/model_version/request_id. |
| Experiment information / evaluation | MongoDB configuration and metric snapshots, linked by experiment_id; large artifacts in MinIO; stable model/version provenance in PostgreSQL. |
| Original image retrieval | Authorize using PostgreSQL ownership/ready state, then retrieve MinIO bytes or issue a short-lived URL. |

| Problem | Concrete scenario | Proposed solution |
|---|---|---|
| Performance bottleneck | Repeated 5 MB downloads pass through the API and saturate its network. | Let authorized workers fetch MinIO objects directly, cache hot objects, batch metadata lookups, monitor throughput/latency. |
| Scalability issue | Millions of prediction logs create large indexes and write/analytics contention on one node. | Retain required logs, index real query paths, separate analytics, then shard/partition based on measured distribution; model_version alone may be skewed. |
| Failure scenario | Upload succeeds but metadata finalization or log writing fails, leaving inconsistent cross-store state. | Use pending/ready/error states, idempotent keys, durable outbox/queue retries, reconciliation and checksum checks before ready. Alert on stale pending records. |

Production requires protected endpoints, scoped access, backups and tested restoration for all stores. A one-node Compose demo does not establish production availability.

**Final answer:** SQL, NoSQL and object storage can be more effective together because their data models fit different workloads: relational consistency and metadata search, flexible evolving documents, and large independent binaries. This enables separate scaling and retention while reducing contention. The tradeoff is operational complexity and explicit cross-store consistency handling.''')
md('''## Evidence and reproducibility

Primary instruction: supplied `LAB_2.pdf`, eight pages. Background context: [Smart Campus repository](https://github.com/megamind294/Smart-Campus-Student-Life-Management-System).

The runner stores complete results in `lab2_execution/evidence/`: PostgreSQL query rows, MongoDB seed documents and query results, MinIO object listings, combined retrieval and verification checks. Actual run time is recorded separately from synthetic fixture dates.

Prepared with AI assistance for code and report assembly. No unperformed task is claimed as completed. After successful execution, save the notebook with its outputs before submission. Only one person submits the group report.

To stop this isolated laboratory after saving evidence, run `docker compose -f lab2_execution/docker-compose.yml stop`. This preserves its named volumes.''')
if done:
    md('## Recorded execution evidence from report preparation')
    for name in ['verification.json','postgres-results.json','mongo-results.json','minio-objects.json','combined-result.json']:
        cells.append({'cell_type':'code','metadata':{},'execution_count':None,'source':[f'# Recorded file: {name}\n'],
        'outputs':[{'output_type':'stream','name':'stdout','text':(ROOT/'evidence'/name).read_text(encoding='utf-8').splitlines(True)}]})
notebook={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'}},'nbformat':4,'nbformat_minor':5}
for i,c in enumerate(cells):c['id']=f'lab2-cell-{i:02d}'
path=OUT/('LAB_2_Rinkle_Sharma_Saisri_Akkireddi.ipynb' if done else 'LAB_2_Rinkle_Sharma_Saisri_Akkireddi_EXECUTION_PENDING.ipynb')
path.write_text(json.dumps(notebook,indent=2),encoding='utf-8')
print(path)
