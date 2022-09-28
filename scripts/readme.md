# Bihar scraper
Scraper for http://epds.bihar.gov.in/DistrictWiseRationCardDetailsBH.aspx listing 

This scraper consists of 2 main parts

1. Scrapy spider to get htmls and data in json

To run it
```
scrapy crawl bihar
```

It will output html files into `html` folder and json data into `parsed/extracted.json` file


2. Parser 

To run it
```
parser/main.py
```

It will output csvs for every table in the site and one for every contact in the parsed folder
