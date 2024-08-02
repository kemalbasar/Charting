WITH ShiftData AS (
  SELECT
    MATERIAL,
    CONFIRMATION,
	MIN(CURDATETIME) AS STARTTIME,
	MAX(CURDATETIME) AS ENDTIME,
	COUNT(CONFIRMATION) AS QUANTITY,
	NOTOKGORSEL,
	NOTOKOLCUSEL,
    CASE
            WHEN CAST(CURDATETIME AS TIME) >= '07:00' AND CAST(CURDATETIME  AS TIME) < '15:00' THEN 1
            WHEN (CAST(CURDATETIME  AS TIME) >= '15:00' AND CAST(CURDATETIME  AS TIME) < '23:00') THEN 2
            WHEN (CAST(CURDATETIME  AS TIME) >= '23:00' OR CAST(CURDATETIME  AS TIME) < '07:00') THEN 3
      ELSE 3
    END AS SHIFTAYK
  FROM [dbo].[XYZ] 
     WHERE CURDATETIME >= 'XXXX-XX-XX 07:00' AND CURDATETIME < 'YYYY-YY-YY 07:00'
    AND CONFIRMATION != 0
  GROUP BY     MATERIAL,
    CONFIRMATION,
	NOTOKGORSEL,
	NOTOKOLCUSEL,
	CURDATETIME
)
SELECT DISTINCT 'XYZ' AS MACHINE,AYK.AYKDATE,AYK.SHIFTAYK AS SHIFTURETIM,(CONF.NAME + ' '+CONF.SURNAME) AS NAME,P.MATERIAL ,
	 P.PRDORDER , SUM(AYK.QUANTITY) AS QUANTITY,SUM(AYK.NOTOK) AS NOTOK,
	0 AS SANIYE_DENETLENEN,R.MACHINE AS MACHINETIME,
	0 AS PPM
	FROM [VALFSAN604].[dbo].IASPRDORDER P
	LEFT JOIN (SELECT CLIENT,COMPANY, NAME, SURNAME, PERSONELNUM, PRDORDER, POTYPE
			FROM (
				SELECT
					C.CLIENT,C.COMPANY,H.NAME, H.SURNAME,C.PERSONELNUM, C.PRDORDER,C.POTYPE,
					ROW_NUMBER() OVER (PARTITION BY C.PRDORDER ORDER BY C.PERSONELNUM) AS RowNum
				FROM [VALFSAN604].[dbo].IASPRDCONF C
				LEFT JOIN [VALFSAN604].[dbo].IASHCMPERS H ON C.CLIENT = H.CLIENT
					AND C.PERSONELNUM = H.PERSID
				WHERE C.WORKCENTER LIKE ('KMR-%') AND H.NAME IS NOT NULL
					AND C.OUTPUT > 0
			) AS RankedResults
			WHERE RowNum = 1
			GROUP BY  CLIENT, COMPANY,  NAME,SURNAME, PERSONELNUM,PRDORDER, POTYPE) CONF ON P.CLIENT = CONF.CLIENT
		AND P.COMPANY = CONF.COMPANY
		AND P.PRDORDER = CONF.PRDORDER
		AND P.POTYPE = CONF.POTYPE
	LEFT JOIN (

SELECT
  CAST(MIN(STARTTIME) AS DATE) AS AYKDATE,
  SHIFTAYK,

	MATERIAL,
  CONFIRMATION,
  SUM(QUANTITY) AS QUANTITY,
  (MAX(NOTOKGORSEL)+MAX(NOTOKOLCUSEL)) AS NOTOK
FROM ShiftData
WHERE MATERIAL IS NOT NULL
  AND STARTTIME >= 'XXXX-XX-XX 07:00' AND STARTTIME < 'YYYY-YY-YY 07:00'
GROUP BY
  SHIFTAYK,
  MATERIAL,
  CONFIRMATION
) AYK ON CONF.PRDORDER = AYK.CONFIRMATION
LEFT JOIN  (SELECT CLIENT , COMPANY , MATERIAL , MACHINE FROM [VALFSAN604].[dbo].IASROUOPR WHERE COSTCENTER = 'KMR-AYK') R
ON P.CLIENT = R.CLIENT AND P.COMPANY = R.COMPANY AND P.MATERIAL = R.MATERIAL
		WHERE P.POTYPE = 'N2'
		AND AYK.CONFIRMATION IS NOT NULL
		GROUP BY  AYK.AYKDATE,AYK.SHIFTAYK,(CONF.NAME + ' '+CONF.SURNAME),P.MATERIAL ,
	 P.PRDORDER,R.MACHINE;