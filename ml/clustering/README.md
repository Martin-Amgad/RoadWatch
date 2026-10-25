# Potential duplicate grouping

Implement geographic clustering with DBSCAN over report coordinates. The project plan specifies the haversine metric with coordinates converted to radians and configurable distance (`eps`) and `min_samples`.

Clusters indicate reports that are geographically close, **not confirmed duplicates**. Keep original reports individually accessible; never automatically delete or permanently merge them. Test coordinate conversion, boundary cases, and unclustered/noise reports.
