## Transaction Level Ration Card Data From Bihar (2022)

We scraped http://epds.bihar.gov.in/DistrictWiseRationCardDetailsBH.aspx to get ration card data along with all the details about the beneficiary.

### Scripts

* [Scripts](scripts/)

### Data

The quantitative data are available to researchers with an approved IRB request at the Harvard Dataverse at: https://doi.org/10.7910/DVN/CAVZMQ

The rural and urban files are separately stored. The data are nested with each layer stored in a separate file.

The Urban data is structured as follows:
State -> District -> Nagarpalika -> Ward -> FPS -> Ration Card -> Ration Card Data 

The Rural data is structured as follows:
State -> District -> Panchayat -> Village -> FPS -> Ration Card -> Ration Card Data


