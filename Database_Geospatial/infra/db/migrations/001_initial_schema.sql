CREATE SCHEMA IF NOT EXISTS extensions;
CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA extensions;

CREATE TABLE IF NOT EXISTS public.reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    image_path TEXT NOT NULL CHECK (image_path <> ''),
    latitude DOUBLE PRECISION NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude DOUBLE PRECISION NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    location extensions.geography(Point, 4326) GENERATED ALWAYS AS (
        extensions.ST_SetSRID(
            extensions.ST_MakePoint(longitude, latitude), 4326
        )::extensions.geography
    ) STORED,
    description VARCHAR(1000),
    category VARCHAR(80),
    severity VARCHAR(10) NOT NULL DEFAULT 'none'
        CHECK (severity IN ('none', 'low', 'medium', 'high')),
    severity_score DOUBLE PRECISION,
    severity_rank SMALLINT GENERATED ALWAYS AS (
        CASE severity
            WHEN 'high' THEN 3
            WHEN 'medium' THEN 2
            WHEN 'low' THEN 1
            ELSE 0
        END
    ) STORED,
    status VARCHAR(20) NOT NULL DEFAULT 'submitted'
        CHECK (status IN ('submitted', 'under_review', 'resolved')),
    cluster_label INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID NOT NULL UNIQUE REFERENCES public.reports(id) ON DELETE CASCADE,
    detections JSONB NOT NULL DEFAULT '[]'::jsonb
        CHECK (jsonb_typeof(detections) = 'array'),
    model_version TEXT NOT NULL DEFAULT 'unknown',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE public.reports, public.analyses FROM anon, authenticated;
