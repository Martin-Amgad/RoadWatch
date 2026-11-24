import argparse
import io
import os
import random
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
SEVERITIES = ('high', 'medium', 'low', 'none')
CATEGORIES = ('D00', 'D10', 'D20', 'D40', None)
STATUSES = ('submitted', 'under_review', 'resolved')


def make_demo_rows(base_lat=30.0444, base_lon=31.2357, count=20):
    randomizer = random.Random(2403)
    rows = []
    for index in range(count):
        group = index % 4
        shift_lat = (group - 1) * 0.006
        shift_lon = (group - 1) * 0.008
        lat = base_lat + shift_lat + randomizer.uniform(-0.0002, 0.0002)
        lon = base_lon + shift_lon + randomizer.uniform(-0.0002, 0.0002)
        category = CATEGORIES[index % len(CATEGORIES)]
        severity = SEVERITIES[index % len(SEVERITIES)]
        report_id = uuid5(NAMESPACE_URL, f'roadwatch-member3-demo-report-{index:02d}')
        rows.append({
            'id': report_id,
            'image_path': f'reports/demo/{report_id}.png',
            'latitude': lat,
            'longitude': lon,
            'description': f'SYNTHETIC DEMO REPORT {index + 1:02d}; not an actual road damage event.',
            'category': category,
            'severity': severity,
            'severity_score': None,
            'status': STATUSES[index % len(STATUSES)],
            'cluster_label': None,
            'detections': [] if category is None else [{
                'class_name': category,
                'confidence': 0.8,
                'bbox': [0.1, 0.1, 0.5, 0.5],
            }],
        })
    return rows


def placeholder_png(index):
    from PIL import Image, ImageDraw

    img = Image.new('RGB', (900, 550), (233, 237, 241))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((25, 25, 875, 525), radius=25, outline=(55, 75, 100), width=5)
    draw.text((80, 180), 'ROADWATCH  |  DEMO ONLY', fill=(27, 54, 88), stroke_width=0)
    draw.text((80, 240), f'Synthetic report #{index:02d}', fill=(27, 54, 88))
    draw.text((80, 305), 'Placeholder image - NOT a real road photograph', fill=(80, 80, 80))
    output = io.BytesIO()
    img.save(output, format='PNG')
    return output.getvalue()


def upload_demo_images(rows, url, secret, bucket):
    from supabase import create_client

    if not url or not secret:
        raise SystemExit('SUPABASE_URL and SUPABASE_SECRET_KEY required for --upload-images')
    client = create_client(url, secret)
    store = client.storage.from_(bucket)
    for index, row in enumerate(rows, start=1):
        store.upload(
            path=row['image_path'],
            file=placeholder_png(index),
            file_options={'content-type': 'image/png', 'upsert': 'true'},
        )
    print(f'Uploaded {len(rows)} clearly labeled placeholder images to {bucket}')


def main():
    import psycopg
    from psycopg.types.json import Jsonb

    parser = argparse.ArgumentParser()
    parser.add_argument('--upload-images', action='store_true')
    parser.add_argument('--count', type=int, default=20)
    args = parser.parse_args()
    if not 1 <= args.count <= 100:
        parser.error('count must be between 1 and 100')
    load_dotenv(ROOT / '.env')
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise SystemExit('DATABASE_URL is missing')
    lat = float(os.getenv('DEMO_BASE_LAT', '30.0444'))
    lon = float(os.getenv('DEMO_BASE_LON', '31.2357'))
    rows = make_demo_rows(lat, lon, args.count)
    if args.upload_images:
        upload_demo_images(
            rows,
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_SECRET_KEY'),
            os.getenv('SUPABASE_BUCKET', 'road-images'),
        )
    with psycopg.connect(
        database_url,
        sslmode=os.getenv('DB_SSLMODE', 'require'),
        connect_timeout=10,
    ) as connection:
        with connection.cursor() as cursor:
            inserted = 0
            for row in rows:
                cursor.execute('''
                    INSERT INTO public.reports (
                        id, image_path, latitude, longitude, description,
                        category, severity, severity_score, status, cluster_label
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    RETURNING id
                ''', (
                    row['id'], row['image_path'], row['latitude'], row['longitude'],
                    row['description'], row['category'], row['severity'],
                    row['severity_score'], row['status'], row['cluster_label'],
                ))
                if cursor.fetchone():
                    inserted += 1
                cursor.execute('''
                    INSERT INTO public.analyses (report_id, detections, model_version)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (report_id) DO NOTHING
                ''', (row['id'], Jsonb(row['detections']), 'synthetic-demo'))
    print(f'Seed finished: {inserted} new reports, {len(rows) - inserted} previously present')
    if not args.upload_images:
        print('Image paths are synthetic. Run with --upload-images for actual placeholder objects.')


if __name__ == '__main__':
    main()
