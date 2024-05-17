SELECT MATGRP2,[3],[4],[5] -- Replace these years with the actual year values relevant to your data
FROM
(
    SELECT MATGRP2, PMONTH, ROWBALANCE
    FROM VLFCOMPONENT
    WHERE PMONTH > MONTH(DATEADD(MONTH, -3, GETDATE())) AND
		PYEAR = YEAR(DATEADD(MONTH, -3, GETDATE()))
) AS SourceTable
PIVOT
(
    SUM(ROWBALANCE)
    FOR PMONTH IN ([3],[4],[5])  -- This should match the years in the SELECT clause
) AS PivotTable;