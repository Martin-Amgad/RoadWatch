# RoadWatch — Member 3: Database & Geospatial Data

النسخة دي خاصة بمسؤولية Member 3: PostgreSQL، PostGIS، Supabase Storage configuration، migrations، repository، spatial queries، seed data، والاختبارات.

**حالة مشروع Supabase الحالي:** تم إنشاء `reports` و`analyses`، وتفعيل PostGIS، وإنشاء الـprivate bucket `road-images`، وإضافة دالتي البحث الجغرافي وترتيب الأولوية. ملفات الـmigrations المحلية محدثة لتتوافق مع الحالة دي.

## Quick start — Windows 11 / PowerShell

افتح PowerShell داخل مجلد `RoadWatch_Member3` ونفّذ:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

افتح `.env` واملأ القيم:

- `DATABASE_URL`: انسخ URI كاملًا من Supabase → Connect → Session pooler → URI. استبدل مكان `[YOUR-PASSWORD]` بباسورد قاعدة البيانات الجديد. لا تخمّن الـhost أو username ولا ترسل الرابط لأي شخص.
- `DB_SSLMODE=require`: اتركه كما هو.
- `SUPABASE_URL`: رابط المشروع موجود مسبقًا في `.env.example`؛ تأكد أنه مطابق للوحة التحكم.
- `SUPABASE_SECRET_KEY`: مفتاح Secret API من Project Settings → API Keys. مطلوب لسكريبتات Storage فقط، ويظل على السيرفر.
- `SUPABASE_BUCKET=road-images`: اتركه كما هو.
- `DEMO_BASE_LAT` و`DEMO_BASE_LON`: إحداثيات مركز البيانات التجريبية، ويمكن تغييرها لاحقًا.

**مهم:** المشروع يستخدم Psycopg 3 باسم `psycopg`، وليس `psycopg2`. لا تستخدم تثبيتًا عامًا خارج `.venv`. نفّذ تثبيت المكتبات من `requirements.txt`.

## Run order for the current Supabase project

نفّذ الأوامر دي بالترتيب بعد ضبط `.env`:

```powershell
python scripts/check_env.py
python scripts/apply_migrations.py
python -m pytest -q
python scripts/check_db.py
```

- `check_env.py` يتأكد من وجود الإعدادات، ولا يعرض كلمة المرور أو المفتاح السري.
- `apply_migrations.py` ينشئ `public.schema_migrations` ويسجل ملفات SQL المحلية. Migration 001 و002 تستخدمان `IF NOT EXISTS`، وMigration 003 تستخدم `CREATE OR REPLACE` للدوال الموجودة بالفعل وتعيد تأكيد صلاحيات `service_role`.
- `pytest` يشغّل الاختبارات المحلية.
- `check_db.py` يختبر اتصال PostgreSQL ووجود PostGIS والجداول والاستعلامات.

الـbucket `road-images` موجود بالفعل في مشروعك وهو Private؛ لذلك لا تحتاج تشغيل `python scripts/create_bucket.py` حاليًا. لو أعدت إنشاء مشروع مختلف، شغّل السكريبت بعد إضافة `SUPABASE_SECRET_KEY`.

## Demo data — لا تشغّلها على Production بدون موافقة الفريق

السكريبت التالي يضيف 20 بلاغًا اصطناعيًا ويرفع صور Placeholder مكتوب عليها DEMO ONLY:

```powershell
python scripts/seed_reports.py --upload-images
```

مشروع Supabase الحالي على فرع `main` المعلّم Production؛ لذلك لا تشغّل الأمر إلا بعد موافقة الفريق على إضافة بيانات تجريبية إلى قاعدة البيانات دي.

## Pending image cleanup

للمعاينة فقط:

```powershell
python scripts/cleanup_pending.py
```

ده Dry Run ولا يحذف أي ملفات. لا تستخدم `--apply` إلا بعد مراجعة الملفات المرشحة للحذف وموافقة الفريق.

## Files

| File | Purpose |
|---|---|
| `infra/db/migrations/001_initial_schema.sql` | جدول reports وanalyses، PostGIS location، checks وRLS |
| `infra/db/migrations/002_indexes.sql` | GiST spatial وB-tree indexes |
| `infra/db/migrations/003_spatial_functions_and_backend_grants.sql` | spatial functions وصلاحيات backend |
| `infra/db/repository.py` | CRUD وspatial وcluster data access |
| `infra/db/validation.py` | التحقق من الإحداثيات والحالات والمعاملات |
| `scripts/apply_migrations.py` | تطبيق migrations وتسجيل checksums |
| `scripts/check_env.py` | فحص الإعدادات بدون عرض الأسرار |
| `scripts/check_db.py` | اختبار اتصال قاعدة البيانات والاستعلامات |
| `scripts/create_bucket.py` | إنشاء private Storage bucket عند الحاجة |
| `scripts/seed_reports.py` | إنشاء 20 بلاغًا اصطناعيًا للاختبار |
| `scripts/cleanup_pending.py` | معاينة/تنظيف صور pending الأقدم من 24 ساعة |
| `tests/` | اختبارات Python المحلية |
| `docs/HANDOFF_TO_MEMBER2.md` | عقد التكامل مع Member 2 |
| `docs/DATABASE_DESIGN.md` | تصميم قاعدة البيانات وتدفق البيانات |
| `docs/DECISIONS_TO_CONFIRM.md` | القرارات التي يجب تأكيدها مع الفريق |

## Scope boundaries

- Member 3: PostgreSQL/PostGIS، migrations، repository، تخزين البيانات، seed data والاختبارات.
- Member 2: FastAPI، المصادقة، رفع الصور، واستدعاء وظائف التحليل.
- Member 4: YOLO/detection والتقييم.
- Member 5: severity وDBSCAN.
- Member 6: Dashboard والنشر والـE2E.

لا تضع `.env` أو أي credentials في GitHub. لا ترسل `SUPABASE_SECRET_KEY` أو `DATABASE_URL` إلى Flutter أو Dashboard. راجع `docs/HANDOFF_TO_MEMBER2.md` قبل دمج الـAPI.
