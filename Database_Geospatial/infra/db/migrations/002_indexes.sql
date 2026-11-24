CREATE INDEX IF NOT EXISTS idx_reports_location_gist
    ON public.reports USING GIST (location);

CREATE INDEX IF NOT EXISTS idx_reports_priority_created
    ON public.reports (severity_rank DESC, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_reports_status_priority
    ON public.reports (status, severity_rank DESC, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_reports_category
    ON public.reports (category);

CREATE INDEX IF NOT EXISTS idx_reports_cluster_label
    ON public.reports (cluster_label)
    WHERE cluster_label IS NOT NULL;
