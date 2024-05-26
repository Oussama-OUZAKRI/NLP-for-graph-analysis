import json

def edges_generator():
    vertices = []

    # Read JSON data
    with open('C:\\Users\\Oussama Ouzakri\\scrapy_tutorials\\wikipediascraper\\data_city.json', "r", encoding="utf-8") as file:
        cityData = json.load(file)
        city_company = [list(city.keys())[0] for city in cityData if city]  # Ensure the city dictionary is not empty
        
    with open('C:\\Users\\Oussama Ouzakri\\scrapy_tutorials\\wikipediascraper\\data_company.json', "r", encoding="utf-8") as file:
        companyData = json.load(file)
        company_company = [company.get('Company') for company in companyData]
        
    with open('C:\\Users\\Oussama Ouzakri\\scrapy_tutorials\\wikipediascraper\\data_person.json', "r", encoding="utf-8") as file:
        personData = json.load(file)
        person_company = [list(person.keys())[0] for person in personData if person]  # Ensure the person dictionary is not empty

    for company in companyData:
        company_name = company.get('Company')

        # Link companies to their headquarters cities
        if company_name in city_company:
            for city in cityData:
                if company_name in city:
                    for city_info in city[company_name] : # Access elements of the city info list
                        relation = {'source': company_name, 'destination': city_info['City'], 'relation': 'Headquarters'}
                        vertices.append(relation)
        elif 'Headquarters' in company:
            relation = {'source': company_name, 'destination': company['Headquarters'], 'relation': 'Headquarters'}
            vertices.append(relation)

        # Link companies to key people
        if company_name in person_company:
            for person in personData:
                if company_name in person:
                    for person_info in person[company_name] : # Access the first element of the person info list
                        relation = {'source': company_name, 'destination': person_info['name'], 'relation': 'Key-People'}
                        vertices.append(relation)
        elif 'Key people' in company:
            relation = {'source': company_name, 'destination': company['Key people'], 'relation': 'Key-People'}
            vertices.append(relation)
        elif 'Founder' in company:
            relation = {'source': company_name, 'destination': company['Founder'], 'relation': 'Founder'}
            vertices.append(relation)

        # Link companies to their owners
        if 'Owner' in company:
            relation = {'source': company_name, 'destination': company.get('Owner'), 'relation': 'Owner'}
            vertices.append(relation)
    
    # Write the vertices to a new JSON file
    with open('C:\\Users\\Oussama Ouzakri\\scrapy_tutorials\\wikipediascraper\\edges_data.json', 'w', encoding='utf-8') as f:
        json.dump(vertices, f, ensure_ascii=False, indent=4)

# Run the function
edges_generator()
