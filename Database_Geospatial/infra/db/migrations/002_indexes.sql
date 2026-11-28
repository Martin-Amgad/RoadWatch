CREATE INDEX IF NOT EXISTS analyses_created_at_idx
    ON public.analyses (created_at);

CREATE INDEX IF NOT EXISTS reports_location_idx
    ON public.reports USING GIST (location);

CREATE INDEX IF NOT EXISTS reports_severity_score_idx
    ON public.reports (severity_score DESC, created_at DESC);

CREATE INDEX IF NOT EXISTS reports_status_idx
    ON public.reports (status);

CREATE INDEX IF NOT EXISTS reports_damage_category_idx
    ON public.reports (damage_category);

CREATE INDEX IF NOT EXISTS reports_cluster_id_idx
    ON public.reports (cluster_id);