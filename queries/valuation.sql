SELECT B.COMPANY, A.MATERIAL, B.WAREHOUSE,SUM(B.SKQUANTITY * (1 - 2 * B.QPOSTWAY)) AS QUANTITY,
                A.MATTYPE, A.MATGRP2 AS MATGRP, T1.MATACGRP, T1.STEXT AS MALCINSI,A.CATEGORY,
                CASE WHEN (SELECT TOP 1 IASVERITEM.PRICE AS PRICE 
                FROM IASVERITEM , IASMATBASIC , IASVERHEAD 
                WHERE IASVERHEAD.CLIENT = '00' 
                               AND IASVERHEAD.COMPANY = '01' 
                               AND IASVERHEAD.COMPANY = IASMATBASIC.COMPANY 
                               AND IASVERHEAD.CLIENT = IASMATBASIC.CLIENT 
                               AND IASVERITEM.PURINVNUM = IASVERHEAD.PURINVNUM 
                               AND IASVERHEAD.EINVOTYPE >= 0 
                               AND IASVERHEAD.DOCRESPONSE >= 0 
                               AND IASVERITEM.MATERIAL = IASMATBASIC.MATERIAL 
                               AND IASVERITEM.COMPANY = IASVERHEAD.COMPANY 
                               AND IASVERITEM.PURINVTYPE = IASVERHEAD.PURINVTYPE 
                               AND IASVERITEM.CLIENT = IASVERHEAD.CLIENT 
                               AND IASVERITEM.MATERIAL = IASMATBASIC.MATERIAL 
                               AND IASVERITEM.CLIENT = IASVERHEAD.CLIENT 
                               AND IASVERHEAD.COMPANY = '01' 
                               AND IASVERHEAD.VENDOR <> '30000096' 
                               AND IASVERITEM.MATERIAL = A.MATERIAL 
                               AND IASVERITEM.COMPANY = B.COMPANY  ORDER BY IASVERITEM.CREATEDAT DESC) IS NOT NULL 
                               THEN (SELECT TOP 1 CONVERT(MONEY,(CASE WHEN IASVERHEAD.CURRENCY = 'TL' THEN CONVERT(MONEY, IASVERITEM.PRICE / IASVERITEM.PUNIT) 
																									ELSE (CONVERT(MONEY,IASVERITEM.PRICE * IB.EXCHRATEPUR / IASVERITEM.PUNIT)) END)/ID.EXCHRATEPUR) AS PRICE 
				FROM IASVERITEM , IASMATBASIC , IASVERHEAD 
                LEFT OUTER JOIN IASBAS012 IB ON (IB.CURDATE = IASVERHEAD.CURRDATE 
                               AND IB.CURRENCY = IASVERHEAD.CURRENCY 
                               AND IB.COMPANY = IASVERHEAD.COMPANY) 
                LEFT OUTER JOIN IASBAS012 ID ON (ID.CURDATE = IASVERHEAD.CURRDATE 
                               AND ID.CURRENCY ='EUR' 
                               AND ID.COMPANY = IASVERHEAD.COMPANY) WHERE IASVERHEAD.CLIENT = '00' 
                               AND IASVERHEAD.COMPANY = '01' 
                               AND IASVERHEAD.COMPANY = IASMATBASIC.COMPANY 
                               AND IASVERHEAD.CLIENT = IASMATBASIC.CLIENT 
                               AND IASVERITEM.PURINVNUM = IASVERHEAD.PURINVNUM 
                               AND IASVERHEAD.EINVOTYPE >= 0 
                               AND IASVERHEAD.DOCRESPONSE >= 0 
                               AND IASVERITEM.MATERIAL = IASMATBASIC.MATERIAL 
                               AND IASVERITEM.COMPANY = IASVERHEAD.COMPANY 
                               AND IASVERITEM.PURINVTYPE = IASVERHEAD.PURINVTYPE 
                               AND IASVERITEM.CLIENT = IASVERHEAD.CLIENT 
                               AND IASVERITEM.MATERIAL = IASMATBASIC.MATERIAL 
                               AND IASVERITEM.CLIENT = IASVERHEAD.CLIENT 
                               AND IASVERHEAD.COMPANY = '01' 
                               AND IASVERHEAD.VENDOR <> '30000096' 
                               AND IASVERITEM.MATERIAL = A.MATERIAL 
                               AND IASVERITEM.COMPANY = B.COMPANY GROUP BY IASVERITEM.MATERIAL, IASVERHEAD.CURRENCY, IASVERITEM.COMPANY, IASVERITEM.CREATEDAT,ID.EXCHRATEPUR , IASVERITEM.PRICE , IASVERITEM.PUNIT,IB.EXCHRATEPUR ORDER BY IASVERITEM.CREATEDAT DESC) ELSE (SELECT TOP 1 CONVERT(MONEY,(CASE WHEN VLFMALFIYAT.CURRENCY = 'TL' THEN CONVERT(MONEY, VLFMALFIYAT.PRICE / VLFMALFIYAT.PUNIT) ELSE (CONVERT(MONEY,VLFMALFIYAT.PRICE * IB.EXCHRATEPUR / VLFMALFIYAT.PUNIT)) END)/ID.EXCHRATEPUR) AS MLINFIYATI  FROM  VLFMALFIYAT 
                LEFT OUTER JOIN IASBAS012 IB ON (IB.CURDATE = CONVERT(DATE,GETDATE()) 
                               AND IB.CURRENCY = VLFMALFIYAT.CURRENCY 
                               AND IB.COMPANY = VLFMALFIYAT.COMPANY) 
                LEFT OUTER JOIN IASBAS012 ID ON (ID.CURDATE =CONVERT(DATE,GETDATE()) 
                               AND ID.CURRENCY ='EUR' 
                               AND ID.COMPANY = VLFMALFIYAT.COMPANY) 
                               WHERE VLFMALFIYAT.MATERIAL=A.MATERIAL 
                               AND VLFMALFIYAT.COMPANY=A.COMPANY ORDER BY VLFMALFIYAT.CREATEDAT DESC) END AS PRICE     
                               
FROM  IASMATBASIC A ,IASINVITEM B 

LEFT OUTER JOIN (SELECT IASMATFMS.COMPANY, IASMATFMS.PLANT, IASMATFMS.MATACGRP, IASMATFMS.MATERIAL, IASBAS034.STEXT, IASMATFMS.FINCURRENCY FROM IASMATFMS , IASBAS034 , IASMATBASIC WHERE IASMATBASIC.CLIENT = IASMATFMS.CLIENT 
                               AND IASMATBASIC.COMPANY = IASMATFMS.COMPANY 
                               AND IASMATBASIC.MATERIAL = IASMATFMS.MATERIAL 
                               AND IASBAS034.COMPANY = IASMATBASIC.COMPANY 
                               AND IASBAS034.MATTYPE = IASMATBASIC.MATTYPE 
                               AND IASBAS034.COMPANY = IASMATFMS.COMPANY 
                               AND IASBAS034.MATACGRP = IASMATFMS.MATACGRP 
                               AND IASBAS034.STEXT <> '') T1 ON T1.COMPANY = B.COMPANY 
                               AND B.PLANT = T1.PLANT 
                               AND B.MATERIAL = T1.MATERIAL

WHERE   B.CLIENT = '00' 
                               AND B.COMPANY = '01' 
                               AND B.PLANT = '01' 
                               AND B.WAREHOUSE!='BKM' 
                AND A.ISDELETE=0
                               AND B.DOCDATE <= GETDATE()
                               AND B.ISCANCELED = 0 
                               AND A.MATERIAL = B.MATERIAL 
                               AND B.COMPANY = A.COMPANY 
                               AND B.CLIENT = A.CLIENT 
                               AND A.ISDELETE = 0 
                               AND B.WAREHOUSE != 'BKM'
                               AND B.WAREHOUSE != 'GTP'
GROUP BY B.COMPANY, B.PLANT, B.WAREHOUSE,B.SPECIALSTOCK, A.MATERIAL, A.COMPANY,B.ISVARIANT, B.VARIANTKEY, B.VOPTIONS ,A.MATTYPE,A.MATGRP2 ,T1.MATACGRP, T1.STEXT,A.CATEGORY
HAVING SUM(B.SKQUANTITY * (1 - 2 * B.QPOSTWAY))> 0 
ORDER BY B.COMPANY, A.MATERIAL;
