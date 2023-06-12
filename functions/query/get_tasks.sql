SELECT 
  13 AS id_agent, 
  SUM(
    CASE WHEN (
      MONTH(start) = 12 
      AND YEAR(start) = 2022
    ) THEN 1 ELSE 0 END
  ) AS assigned_tasks, 
  SUM(
    CASE WHEN (
      complete_date 
      AND MONTH(complete_date) = 12 
      AND YEAR(complete_date) = 2022
    ) THEN 1 ELSE 0 END
  ) AS completed_tasks, 
  ROUND(
    (
      SUM(
        CASE WHEN (complete_date > end) THEN 1 ELSE 0 END
      ) / SUM(
        CASE WHEN (
          MONTH(start) = 12 
          AND YEAR(start) = 2022
        ) THEN 1 ELSE 0 END
      )
    ), 
    2
  ) AS overdue_tasks_percentage 
FROM 
  tasks 
WHERE 
  worker_id = 13
