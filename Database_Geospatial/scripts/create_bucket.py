import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


def main():
    load_dotenv(ROOT / '.env')
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SECRET_KEY')
    bucket = os.getenv('SUPABASE_BUCKET', 'road-images')
    if not url or not key:
        raise SystemExit('SUPABASE_URL and SUPABASE_SECRET_KEY are required')
    from supabase import create_client

    storage = create_client(url, key).storage
    for existing in storage.list_buckets():
        name = existing.get('name') if isinstance(existing, dict) else getattr(existing, 'name', None)
        if name == bucket:
            is_public = existing.get('public') if isinstance(existing, dict) else getattr(existing, 'public', None)
            if is_public:
                raise SystemExit(f'Bucket {bucket} is public. Set it to Private in Supabase first.')
            print(f'Private bucket already exists: {bucket}')
            return
    storage.create_bucket(bucket, options={
        'public': False,
        'allowed_mime_types': ['image/jpeg', 'image/png', 'image/webp'],
        'file_size_limit': 10 * 1024 * 1024,
    })
    print(f'Created private storage bucket: {bucket}')


if __name__ == '__main__':
    main()
