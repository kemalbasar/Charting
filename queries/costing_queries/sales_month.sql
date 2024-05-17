SELECT MATGRP2,[3],[4],[5] -- Replace these years with the actual year values relevant to your data
FROM
(
    SELECT MATGRP2, MONTH, EURBALANCE
    FROM VLFSALESFORCOSTING
    WHERE MONTH > MONTH(DATEADD(MONTH, -3, GETDATE())) AND
		YEAR = YEAR(DATEADD(MONTH, -3, GETDATE()))
) AS SourceTable
PIVOT
(
    SUM(EURBALANCE)
    FOR MONTH IN ([3],[4],[5])  -- This should match the years in the SELECT clause
) AS PivotTable;
