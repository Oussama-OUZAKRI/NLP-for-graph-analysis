import scrapy, json, re
from bs4 import BeautifulSoup

class DataspiderSpider(scrapy.Spider):
    name = "dataSpider"
    start_urls = ["https://en.wikipedia.org/wiki/List_of_companies_in_Morocco"]
    attrb_dict = ["Key people", "Founder", "Owner", "Founded", "Headquarters"]

    def __init__(self):
        super(DataspiderSpider, self).__init__()
        self.companies = []
        self.persons = []
        self.cities = []

    def close(self, reason):
        with open('data_company.json', 'w', encoding='utf-8') as f:
            json.dump(self.companies, f, ensure_ascii=False, indent=4)
        with open('data_person.json', 'w', encoding='utf-8') as f:
            json.dump(self.persons, f, ensure_ascii=False, indent=4)
        with open('data_city.json', 'w', encoding='utf-8') as f:
            json.dump(self.cities, f, ensure_ascii=False, indent=4)

    def parse(self, response):
        company_href = response.css('table.wikitable tbody tr td:first-child a::attr(href)').getall()
        for href in company_href :
            lien = response.urljoin(href)
            yield scrapy.Request(lien, callback=self.parseTable) 

    def parseTable(self, response):
        caption = response.css('table[class*=infobox] caption').get() 
        company_name = self.clean_html_tags(caption)
        company_data = {}
        company_data['Company'] = company_name 
        tr_balise = response.xpath('//table[contains(@class, "infobox")]/tbody/tr').getall() #[not(descendant::img)]
        meta_data_1 = {'company_name' : company_name, 'list' :[]}
        meta_data_2 = {'company_name' : company_name, 'list' :[]}
        for tr in tr_balise :
            tr_selector = scrapy.Selector(text=tr)
            th_balise = tr_selector.css('th').get()
            td_balise = tr_selector.css('td').get()
            th_cleaned = self.clean_html_tags(th_balise)
            td_cleaned = self.clean_html_tags(td_balise)
            if th_cleaned == self.attrb_dict[0] or th_cleaned == self.attrb_dict[1] or th_cleaned == self.attrb_dict[2] or th_cleaned == self.attrb_dict[3] or th_cleaned == self.attrb_dict[4]:
                hrefs = tr_selector.css('td a::attr(href)').getall()
                for href in hrefs:
                    lien = response.urljoin(href)
                    if th_cleaned == self.attrb_dict[0] or th_cleaned == self.attrb_dict[1]:
                        yield scrapy.Request(lien, callback=self.parseTable_person, meta = meta_data_1) 
                    elif th_cleaned == self.attrb_dict[2] or th_cleaned == self.attrb_dict[3]:
                        yield scrapy.Request(lien, callback=self.parseTable) 
                    elif th_cleaned == self.attrb_dict[4]:
                        yield scrapy.Request(lien, callback=self.parseTable_city, meta = meta_data_2)
            if th_cleaned and td_cleaned and th_cleaned != 'IATA':
                company_data[th_cleaned] = td_cleaned
        if company_data['Company'] :
            self.companies.append(company_data)
    
    def parseTable_person(self, response):
        company_name = response.meta.get('company_name', 'Unknown')
        l = response.meta.get('list')
        tr_balise = response.xpath('//table[contains(@class, "infobox")]/tbody/tr').getall()
        person_data = {company_name : l}
        person_info = {}
        c = 0
        for tr in tr_balise :
            tr_selector = scrapy.Selector(text=tr)
            th_balise = tr_selector.css('th').get()
            td_balise = tr_selector.css('td').get()
            th_cleaned = self.clean_html_tags(th_balise)
            td_cleaned = self.clean_html_tags(td_balise)
            if th_cleaned  and td_cleaned is None:
                if  c==0 :
                    person_info['name'] = th_cleaned
                    c += 1
                elif th_cleaned == 'Personal details' : continue
                else :
                    person_info['known for'] = th_cleaned
            elif th_cleaned  and td_cleaned is not None:
                person_info[th_cleaned] = td_cleaned
        if person_info :
            person_data[company_name].append(person_info)
            self.persons.append(person_data)

    def parseTable_city(self, response):
        company_name = response.meta.get('company_name', 'Unknown')
        l = response.meta.get('list')
        tr_balise = response.xpath('//table[contains(@class, "infobox")]/tbody/tr').getall() #[not(descendant::img)]
        city_data = {company_name : l}
        city_info = {}
        c = 0
        for tr in tr_balise :
            tr_selector = scrapy.Selector(text=tr)
            th_balise = tr_selector.css('th').get()
            td_balise = tr_selector.css('td').get()
            th_cleaned = self.clean_html_tags(th_balise)
            td_cleaned = self.clean_html_tags(td_balise)
            if th_cleaned :
                if c == 0:
                    city_info["City"] = th_cleaned
                    c += 1
                elif td_cleaned is None : continue
                else :
                    city_info[th_cleaned] = td_cleaned
        if city_info :
            city_data[company_name].append(city_info)
            self.cities.append(city_data)

    def clean_html_tags(self, html_text):
        if not html_text :
            return None
        soup = BeautifulSoup(html_text, 'html.parser')
        for img_tag in soup.find_all('img'):
            img_tag.decompose()
        for tag in soup.find_all('sup'):
            tag.decompose()
        cleaned_text = soup.get_text(separator=' ',strip=True)
        #supprimer les caractères spéciaux
        cleaned_text = re.sub(r'[^\w\s\.\-/\\_%()\'$]', '', cleaned_text)
        return cleaned_text.strip()
