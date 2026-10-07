/*
 Pipeline health: run counts by outcome and success-only duration baseline per job.
 Source: system.lakeflow (job_run_timeline, jobs).
 Notes:
  - Durations cover SUCCEEDED runs only, so failed/cancelled runs don't skew the baseline.
  - Staging and prod have few runs, so treat p95 as a rough baseline, not an SLA.
*/
WITH runs AS (
  SELECT
    j.name AS job_name,
    r.run_id,
    timestampdiff(SECOND, MIN(r.period_start_time), MAX(r.period_end_time)) AS duration_sec,
    MAX_BY(r.result_state, r.period_end_time) AS result_state
  FROM system.lakeflow.job_run_timeline r
  JOIN (
    SELECT job_id, name
    FROM system.lakeflow.jobs
    QUALIFY ROW_NUMBER() OVER (PARTITION BY job_id ORDER BY change_time DESC) = 1
  ) j USING (job_id)
  GROUP BY j.name, r.run_id
)
SELECT
  job_name,
  COUNT(*) AS runs,
  COUNT_IF(result_state = 'SUCCEEDED') AS succeeded,
  COUNT_IF(result_state = 'ERROR') AS errored,
  COUNT_IF(result_state = 'CANCELLED') AS cancelled,
  ROUND(AVG(duration_sec) FILTER (WHERE result_state = 'SUCCEEDED'), 0) AS avg_ok_sec,
  ROUND(PERCENTILE(duration_sec, 0.95) FILTER (WHERE result_state = 'SUCCEEDED'), 0) AS p95_ok_sec
FROM runs
GROUP BY job_name
ORDER BY job_name;