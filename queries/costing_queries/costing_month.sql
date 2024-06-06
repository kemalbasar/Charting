SELECT MATGRP2,[a],[b],[c] -- Replace these years with the actual year values relevant to your data
FROM
(
    SELECT MATGRP2, (CAST(PMONTH AS varchar(10))  + '-' + CAST(PYEAR AS VARCHAR(10)) ) AS PMONTH, ROWBALANCE
    FROM VLFCOMPONENT
    WHERE PMONTH > MONTH(DATEADD(MONTH, -4, GETDATE())) AND
		PYEAR = YEAR(DATEADD(MONTH, -4, GETDATE()))
) AS SourceTable
PIVOT
(
    SUM(ROWBALANCE)
    FOR PMONTH IN ([a],[b],[c])  -- This should match the years in the SELECT clause
) AS PivotTable;


