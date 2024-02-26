SELECT
    "CUST ID#",
    "CUSTOMER NAME",
    "INVOICE DATE",
    "INVOICE NUMBER",
    "INVOICE AMT",
    "INVOICE TAX TOTAL",
    "IND BILL VALUE",
    "IND TAX DLRS",
    "APPLIED AMT",
    "AMOUNT DUE",
    "PO NUMBER",
    "Cust WO# / Tracking #s",
    "DAYS OLD",
    "YYYY-MM",
    "Work Site#",
    "WKS ADDR1",
    "WKS ADDR2",
    "WKS CITY",
    "WKS STATE",
    "Service Description",
    "WO TYP"
FROM
    "2024/02/26 03:30:12PM"
WHERE
    "AMOUNT DUE" > 200
AND
    "CUSTOMER NAME" = "CITY STORAGE SYSTEMS LLC"

####################################################

SELECT "CUST ID#","CUSTOMER NAME","INVOICE DATE","INVOICE NUMBER","INVOICE AMT","INVOICE TAX TOTAL","IND BILL VALUE","IND TAX DLRS","APPLIED AMT","AMOUNT DUE","PO NUMBER","Cust WO# / Tracking #s","DAYS OLD","YYYY-MM","Work Site#","WKS ADDR1","WKS ADDR2","WKS CITY","WKS STATE","Service Description","WO TYP" FROM "2024/02/26 03:30:12PM" WHERE "AMOUNT DUE" > 200 AND "CUSTOMER NAME" = "CITY STORAGE SYSTEMS LLC"