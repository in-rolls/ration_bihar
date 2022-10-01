import scrapy
import json
import re
import urllib.parse

class BiharSpider(scrapy.Spider):
    name = 'bihar'
    allowed_domains = ['epds.bihar.gov.in']
    start_urls = ['http://epds.bihar.gov.in/DistrictWiseRationCardDetailsBH.aspx']
    HTMLS_PATH = '../parsed/htmls/'
    BASE_URL = "http://epds.bihar.gov.in/"
    error_url = []

    def get_req(self, r, form_data, callback, meta):
        id_form_data = form_data.copy()
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        form_data.update({
            '__VIEWSTATE': r.xpath('//input[@id="__VIEWSTATE"]/@value').get(),
            '__VIEWSTATEGENERATOR': r.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value').get(),
            '__VIEWSTATEENCRYPTED': r.xpath('//input[@id="__VIEWSTATEENCRYPTED"]/@value').get(),
            '__EVENTVALIDATION': r.xpath('//input[@id="__EVENTVALIDATION"]/@value').get(),
        })

        if not ':' in r.url:
            breakpoint()

        return scrapy.FormRequest(
            r.url,
            method='POST',
            formdata=form_data,
            callback=callback,
            meta={'id_form_data':id_form_data},
            headers=headers 
        )


    def parse(self, r):
        # Start

        form_data = {
                'ddlDistrict': "0", 
                'btnLoad': "Show"
                }
        meta = {'form_data':form_data}

        yield self.get_req(r, form_data, self.parse_table, meta=meta)
        # yield scrapy.FormRequest.from_response(
        #     r,
        #     formdata=form_data,
        #     callback=self.parse_table,
        #     meta={'form_data':form_data}
        # )
    
    def clean_field(self, f):
        try:
            f = f.replace('+', ' ')
            f = f.replace('%20', ' ')
            f = re.sub('\s+', ' ', f)
            f = f.strip()
            f = urllib.parse.unquote(f)
        except Exception as e:
            print(e)
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

        for row in rows[1:-2]:
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

                    form_data = {
                        '__EVENTTARGET': target, 
                        '__EVENTARGUMENT': argument,
                        #'ddlDistrict': '0'
                    }
                    meta = {'form_data':form_data} 
                    yield self.get_req(r, form_data, self.parse_table, meta=meta)

                    # yield scrapy.FormRequest.from_response(
                    #     r,
                    #     formdata=form_data,
                    #     callback=self.parse_table,
                    #     dont_click=True,
                    #     meta={'form_data':form_data}
                    # )

            json_table.append(item)
        
        # Get last row
        last_row_selector = table.xpath('//table[@id="gridmain"]//tr[last()]/td')
        last_row = last_row_selector.xpath('.//text()').getall()
        last_row = [_.strip() for _ in last_row]
        last_row = ''.join(list(filter(None, last_row)))

        # Catch next page
        next_href = None
        if ('1' in last_row or '...' in last_row) and not last_row_selector.xpath('.//@id').getall() and not 'Total' in last_row:
            next_href = last_row_selector.xpath('.//table/tr/td[descendant::span]/following-sibling::td//@href').get()
            if next_href:
                target, argument = next_href.split("('")[1].split("')")[0].split("','")

                form_data = {
                    '__EVENTTARGET': target, 
                    '__EVENTARGUMENT': argument,
                }
                meta = {
                    'is_next':json_table,
                    'form_data':form_data
                }
                yield self.get_req(r, form_data, self.parse_table, meta=meta)

        if not next_href:
            page = {
                'url': r.url,
                'categories': categories
            }

            if ration_card_data:
                page.update({
                    'ration_card_details': ration_card,
                    'sub_table': json.dumps(json_table),
                    'image_urls': [ration_card['img']]
                })

            else:
                page.update({
                    'table': json.dumps(json_table)
                })
            
            yield page

        # Save html
        file_name = '_'.join([ _[:20] for _ in categories.values()])
        file_path = self.HTMLS_PATH + file_name + '.html'
        with open(file_path, 'wb+') as f:
            f.write(r.body)

        # # TEST 
        # file_path = 'errors.json'
        # with open(file_path, 'w+') as f:
        #     f.write(json.dumps(self.error_url))

        




