WITH ASCD AS (SELECT DISTINCT C.WORKCENTER, CASE WHEN CAST(C.WORKEND AS TIME) > '07:15' AND CAST(C.WORKEND AS TIME)  < '15:15'
THEN 1 ELSE 0 END AS VAR1 ,
 CASE WHEN CAST(C.WORKEND AS TIME) >= '15:15' AND CAST(C.WORKEND AS TIME)  < '23:15' THEN 1 ELSE 0  END AS VAR2,
 CASE WHEN CAST(C.WORKEND AS TIME) > '23:15' AND CAST(C.WORKEND AS TIME)  <= '07:15' THEN 1 ELSE 0  END AS VAR3
 FROM IASPRDCONF C
WHERE  C.COSTCENTER IN ('CNC','TASLAMA','CNCTORNA','MONTAJ')
AND C.WORKSTART > (CASE DATENAME(WEEKDAY, GETDATE()) WHEN 'Monday'
THEN   CAST(CAST(DATEADD(DAY,-3,GETDATE()) AS DATE) AS DATETIME) ELSE  CAST(CAST(DATEADD(DAY,-1,GETDATE()) AS DATE) AS DATETIME)  END))
SELECT WORKCENTER, COUNT(WORKCENTER) AS VARD FROM ASCD GROUP BY WORKCENTER
ORDER BY WORKCENTER

