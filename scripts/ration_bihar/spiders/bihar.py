import scrapy
import json
import re

class BiharSpider(scrapy.Spider):
    name = 'bihar'
    allowed_domains = ['epds.bihar.gov.in']
    start_urls = ['http://epds.bihar.gov.in/DistrictWiseRationCardDetailsBH.aspx']
    HTMLS_PATH = 'htmls/'
    BASE_URL = "http://epds.bihar.gov.in/"
    error_url = []

    def parse(self, r):
        # Start
        yield scrapy.FormRequest.from_response(
            r,
            formdata={
                'ddlDistrict': "0", 
                'btnLoad': "Show"
                },
            callback=self.parse_table
        )
    
    def clean_field(self, f):
        try:
            f = f.replace('+', ' ')
            f = f.replace('%20', ' ')
            f = re.sub('\s+', ' ', f)
            f = f.strip()
        except:
            ...

        return f

    def get_categories(self, url):
        categories = {
            'state': 'Bihar',
        }

        if '/Block_Town_Wise' in url or 'Tahsil_Name_PMO' in url:
            categories['town_wise'] = 'rural'
        elif '/Town_Wise' in url or 'Village_Name_PMO' in url:
            categories['town_wise'] = 'urban'

        if '?' in url:
            try:
                cats = url.split('?')[-1]
                cats = cats.split('&')
                for c in cats:
                    if c:
                        k, v = c.split('=')
                        categories[k] = self.clean_field(v)

            except Exception as e:
                self.logging.error(str(e))

        return categories

    def parse_table(self, r):
        json_table = r.meta.get('is_next', [])

        # Set page item with categories
        categories = self.get_categories(r.url)

        # Try to get ration_card data (only in the ration_card details page)
        ration_card_data = r.xpath('//table[@id="TABLE1"]') 

        if ration_card_data:
            ration_card = {}
            # Get rows
            rows = r.xpath('//table[@id="TABLE1"]/tr')

            # Parse any descriptive row
            for row in rows:
                text = ''.join([ _.strip() for _ in row.xpath('.//text()').getall()])
                if ':' in text:
                    k, v = text.split(':')
                    v = v.strip()
                    k = k.strip()
                    if v != '-':
                        ration_card[k] = v
                
                if img_src := row.xpath('.//img[@id="img_Family"]/@src').get():
                    ration_card['img'] = self.BASE_URL + img_src
                

        # Get full table or table inside details page
        table = r.xpath('//table[@id="gridmain"]')

        # Get first row 
        headers = table.xpath('./tr/th//text()').getall()

        # Get Rows
        rows = table.xpath('.//tr') 

        for row in rows[1:-1]:
            item = {}
            fields = row.xpath('./td')

            for i, cell in enumerate(fields):
                field = cell.xpath('.//text()').getall()
                field = ''.join([_.strip() for _ in field])
                field_href = cell.xpath('.//a/@href').get()
                
                # Store field in dictionary
                if field:
                    item[headers[i]] = field

                # If there's a link, parse it.
                if field_href:
                    target, argument = field_href.split("('")[1].split("')")[0].split("','")

                    try:
                        yield scrapy.FormRequest.from_response(
                            r,
                            formdata={
                                '__EVENTTARGET': target, 
                                '__EVENTARGUMENT': argument,
                                'ddlDistrict': '0'
                                },
                            callback=self.parse_table,
                            dont_click=True,
                        )
                    except:
                        #breakpoint()
                        self.error_url.append(r.url)

            json_table.append(item)
        
        # Get last row
        last_row_selector = table.xpath('//table[@id="gridmain"]//tr[last()]/td')
        last_row = last_row_selector.xpath('.//text()').getall()
        last_row = [_.strip() for _ in last_row]
        last_row = ''.join(list(filter(None, last_row)))

        # Catch next page
        if ('1' in last_row or '...' in last_row) and not last_row_selector.xpath('.//@id').getall() and not 'Total' in last_row:
            # Get next page
            next_href = last_row_selector.xpath('.//@href').get() 
            target, argument = next_href.split("('")[1].split("')")[0].split("','")

            try:
                yield scrapy.FormRequest.from_response(
                    r,
                    formdata={
                        '__EVENTTARGET': target, 
                        '__EVENTARGUMENT': argument,
                        },
                    callback=self.parse_table,
                    dont_click=True,
                    meta={'is_next':json_table}
                )
            except:
                #breakpoint()
                self.error_url.append(r.url)

        else:
            page = {
                'url': r.url,
                'categories': categories
            }

            if ration_card_data:
                page.update({
                    'ration_card_details': ration_card,
                    'sub_table': json.dumps(json_table)
                })

            else:
                page.update({
                    'table': json.dumps(json_table)
                })
            
            yield page

        # Save html
        file_name = '_'.join([ _ for _ in categories.values()])
        file_path = self.HTMLS_PATH + file_name + '.html'
        with open(file_path, 'wb+') as f:
            f.write(r.body)


        




