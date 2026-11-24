SELECT
    id,
    latitude,
    longitude,
    category,
    severity,
    status,
    cluster_label,
    extensions.ST_Distance(
        location,
        extensions.ST_SetSRID(extensions.ST_MakePoint(31.2357, 30.0444), 4326)::extensions.geography
    ) AS distance_m
FROM public.reports
WHERE extensions.ST_DWithin(
    location,
    extensions.ST_SetSRID(extensions.ST_MakePoint(31.2357, 30.0444), 4326)::extensions.geography,
    100
)
ORDER BY distance_m ASC;
