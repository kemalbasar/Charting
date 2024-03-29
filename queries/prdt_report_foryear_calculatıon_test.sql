WITH ASCD AS (SELECT DISTINCT C.WORKCENTER,
CASE WHEN ((CAST(C.WORKSTART AS TIME) >= '06:50' AND CAST(C.WORKSTART AS TIME)  <= '14:50')
OR (CAST(C.WORKEND AS TIME) >= '08:50' AND CAST(C.WORKEND AS TIME)  < '15:15')) THEN 1 ELSE 0 END AS VAR1 ,

 CASE WHEN CAST(C.WORKSTART AS TIME) > '14:50' AND CAST(C.WORKSTART AS TIME)  <= '22:59'
OR  (CAST(C.WORKEND AS TIME) >= '15:16' AND CAST(C.WORKEND AS TIME)  <= '22:50') THEN 1 ELSE 0  END AS VAR2,

  CASE WHEN C.WORKSTART >= '2023-01-03 23:00:00' AND C.WORKSTART   < '2023-01-04 06:50:00'  THEN 1 ELSE 0  END AS VAR3
 FROM IASPRDCONF C
WHERE  C.COSTCENTER IN ('CNC','TASLAMA','CNCTORNA')
AND C.WORKSTART > '2023-01-03 23:00:00'
AND C.WORKSTART < '2023-01-04 23:00:00')

SELECT WORKCENTER, CASE WHEN COUNT(WORKCENTER) >3 THEN 3 ELSE COUNT(WORKCENTER) END AS VARD FROM ASCD
WHERE VAR1 + VAR2 + VAR3 =1 GROUP BY WORKCENTER
