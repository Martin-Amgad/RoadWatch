CREATE SCHEMA IF NOT EXISTS extensions;
CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA extensions;

CREATE TABLE IF NOT EXISTS public.analyses (
    id              UUID PRIMARY KEY,
    created_at      TIMESTAMPTZ      NOT NULL DEFAULT now(),
    image_path      TEXT             NOT NULL,
    image_width     INTEGER          NOT NULL CHECK (image_width > 0),
    image_height    INTEGER          NOT NULL CHECK (image_height > 0),
    detections      JSONB            NOT NULL DEFAULT '[]'::jsonb,
    damage_category TEXT,
    confidence      DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (confidence BETWEEN 0 AND 1),
    severity_label  TEXT             NOT NULL CHECK (severity_label IN ('Low', 'Medium', 'High', 'None')),
    severity_score  DOUBLE PRECISION NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS public.reports (
    id              UUID PRIMARY KEY,
    created_at      TIMESTAMPTZ                       NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ                       NOT NULL DEFAULT now(),
    image_path      TEXT                              NOT NULL,
    location        extensions.geography(Point, 4326) NOT NULL,
    description     TEXT,
    damage_category TEXT,
    confidence      DOUBLE PRECISION                  NOT NULL DEFAULT 0 CHECK (confidence BETWEEN 0 AND 1),
    detections      JSONB                             NOT NULL DEFAULT '[]'::jsonb,
    severity_label  TEXT                              NOT NULL CHECK (severity_label IN ('Low', 'Medium', 'High', 'None')),
    severity_score  DOUBLE PRECISION                  NOT NULL DEFAULT 0,
    status          TEXT                              NOT NULL DEFAULT 'Submitted'
                    CHECK (status IN ('Submitted', 'Under Review', 'Resolved')),
    cluster_id      INTEGER
);

ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports  ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE public.analyses, public.reports FROM anon, authenticated;