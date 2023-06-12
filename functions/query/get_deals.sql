SELECT 
  13 AS id_agent, 
  SUM(
    CASE WHEN (
      MONTH(complete_date) = 12 
      AND YEAR(complete_date) = 2022 
      AND status = 6
    ) THEN 1 ELSE 0 END
  ) AS successful_deals, 
  SUM(
    CASE WHEN (
      MONTH(complete_date) = 12 
      AND YEAR(complete_date) = 2022 
      AND status = 6
    ) THEN price ELSE 0 END
  ) AS profit, 
  ROUND(
    (
      SUM(
        CASE WHEN (
          MONTH(complete_date) = 12 
          AND YEAR(complete_date) = 2022 
          AND status = 6
        ) THEN price ELSE 0 END
      ) / SUM(
        CASE WHEN (
          MONTH(complete_date) = 12 
          AND YEAR(complete_date) = 2022 
          AND status = 6
        ) THEN 1 ELSE 0 END
      )
    ), 
    2
  ) AS average_deal_size 
FROM 
  deals 
WHERE 
  user_id = 13
