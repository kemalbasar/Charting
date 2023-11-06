SELECT FORMAT(IASPRDCONF.WORKSTART ,'yyyy-MM') AS DATE,
CAST(SUM(IASPRDCONF.OUTPUT +IASPRDCONF.SCRAP+IASPRDCONF.REWORK) AS INT) AS QUANTITY,CAST(SUM((IASPRDCONF.OUTPUT +IASPRDCONF.SCRAP+IASPRDCONF.REWORK)*B.BRUTWEIGHT)/1000 AS INT) AS TOTALWEIGHT
FROM IASPRDCONF
LEFT JOIN IASPRDOPR A ON  A.CONFIRMATION = IASPRDCONF.CONFIRMATION
LEFT JOIN IASMATBASIC B ON A.MATERIAL = B.MATERIAL AND B.COMPANY  = '01'
WHERE IASPRDCONF.WORKCENTER IN (XXMATERIALYY)
AND IASPRDCONF.WORKSTART BETWEEN  'xxxx-yy-zz 23:00:00' AND 'aaaa-bb-cc 00:00:00'
GROUP BY FORMAT(IASPRDCONF.WORKSTART,'yyyy-MM')
