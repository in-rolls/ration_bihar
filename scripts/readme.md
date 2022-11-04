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
python3 scripts/parser/main.py
```

It will output all records in a SQLite DB at `parsed/ration_cards.sqlite`. 
Tables are divided into

- ration_card_details
- district 
- town
- village
- fps
- tahsil
- panchayat

