SELECT DISTINCT W.COSTCENTER,A.WORKCENTER,CASE WHEN A.STATUS = 1 THEN 'grey' WHEN A.STATUS = 2 THEN 'blue' WHEN A.STATUS = 3 THEN 'purple' WHEN A.STATUS = 4 THEN 'green' WHEN A.STATUS = 5 THEN 'red'
WHEN A.STATUS = 6 THEN 'darkred' END AS STATUSR ,H.FULLNAME,M.DRAWNUM,X.STEXT FROM IASAUTSTATUS A
LEFT JOIN IASWORKCENT W ON W.WORKCENTER = A.WORKCENTER 
LEFT JOIN IASHCMPERS H ON H.PERSID = A.PERSONNELNO
LEFT JOIN IASPRDOPR P ON P.CONFIRMATION = A.CONFIRMATION
LEFT JOIN IASMATBASIC M ON M.MATERIAL = P.MATERIAL
LEFT JOIN IASPRDFAILURE F ON A.CONFIRMATION = F.CONFIRMATION AND A.CONFIRMPOS = F.CONFIRMPOS AND A.BREAKDOWN = F.BREAKDOWN
LEFT JOIN IASPRD005 X ON F.FAILURECODE = X.FAILURECODE
WHERE W.WCUSAGE != 'BK' AND 
W.COSTCENTER IN ( 'TASLAMA','CNC','CNCTORNA','MONTAJ')
ORDER BY WORKCENTER