# -*- coding: utf-8 -*-
"""
Created on Sun Mar 31 12:54:56 2024

@author: Oussama Ouzakri
"""

from neo4j import GraphDatabase
import json

# Function to create nodes and relationships in Neo4j
def import_json_to_neo4j(uri, username, password):
    # Connect to Neo4j
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    # Read JSON data
    with open('C:\\Users\\Oussama Ouzakri\\scrapy_tutorials\\wikipediascraper\\cities.json', "r", encoding="utf-8") as file:
        cityData = json.load(file)
        
    with open('C:\\Users\\Oussama Ouzakri\\scrapy_tutorials\\wikipediascraper\\data_company.json', "r", encoding="utf-8") as file:
        companyData = json.load(file)
        
    with open('C:\\Users\\Oussama Ouzakri\\scrapy_tutorials\\wikipediascraper\\persons.json', "r", encoding="utf-8") as file:
        personData = json.load(file)
    
    with open('C:\\Users\\Oussama Ouzakri\\scrapy_tutorials\\wikipediascraper\\edges_data.json', "r", encoding="utf-8") as file:
        edges = json.load(file)

    # Function to remove duplicates from a list of dictionaries
    def remove_duplicates(data, key):
        seen = set()
        unique_data = []
        for item in data:
            val = item[key]
            if val not in seen:
                seen.add(val)
                unique_data.append(item)
        return unique_data

    # Remove duplicates in data
    companyData = remove_duplicates(companyData, 'Company')
    personData = remove_duplicates(personData, 'name')
    cityData = remove_duplicates(cityData, 'City')

    # Define Cypher queries
    create_company_query = "MERGE (n:Company {Company: $Company}) ON CREATE SET n += $attributes"
    create_person_query = "MERGE (n:Person {name: $name}) ON CREATE SET n += $attributes"
    create_city_query = "MERGE (n:City {City: $City}) ON CREATE SET n += $attributes"
    create_relationship_company_query = """
        MATCH (a:Company {Company: $source})
        MATCH (b:Company {Company: $target})
        MERGE (a)-[:OWNER]->(b)
    """
    create_relationship_person_query = """
        MATCH (a:Company {Company: $source})
        MATCH (b:Person {name: $target})
        MERGE (a)-[:KEY_PEOPLE]->(b)
    """
    create_relationship_city_query = """
        MATCH (a:Company {Company: $source})
        MATCH (b:City {City: $target})
        MERGE (a)-[:HEADQUARTERS]->(b)
    """
    
    # Iterate through nodes and create them in Neo4j
    with driver.session() as session:
        # Create companies
        for company in companyData:
            session.run(create_company_query, Company=company['Company'], attributes=company)
        
        # Create persons
        for person in personData:
            session.run(create_person_query, name=person['name'], attributes=person)

        # Create cities
        for city in cityData:
            session.run(create_city_query, City=city['City'], attributes=city)

        # Create relationships
        for edge in edges:
            source = edge.get('source')
            dest = edge.get('destination')
            relation = edge.get('relation')
            if relation == "Headquarters":
                session.run(create_relationship_city_query, source=source, target=dest)
            elif relation == "Owner":
                session.run(create_relationship_company_query, source=source, target=dest)
            elif relation in ["Key-People", "Founder"]:
                session.run(create_relationship_person_query, source=source, target=dest)

        # Check for nodes without relationships and create attribute nodes
        for company in companyData:
            company_name = company.get('Company')
            for attribute in ["Key people", "Founder"]:
                if attribute in company and company[attribute]:
                    attribute_value = company[attribute]
                    # Check if there is already a relationship for this attribute
                    result = session.run(
                        "MATCH (a:Company)-[r]->(b:Person) WHERE a.Company = $source AND b.name = $value RETURN count(r)",
                        source=company_name,
                        value=attribute_value
                    ).single()
                    if result and result["count(r)"] == 0:  # No relationship found
                        attrb = {'name': attribute_value}
                        session.run(create_person_query, name=attribute_value, attributes=attrb)
                        session.run(create_relationship_person_query, source=company_name, target=attribute_value)
            
            attribute = "Owner"
            if attribute in company and company[attribute]:
                attribute_value = company[attribute]
                # Check if there is already a relationship for this attribute
                result = session.run(
                    "MATCH (a:Company)-[r:OWNER]->(b:Company) WHERE a.Company = $source AND b.Company = $value RETURN count(r)",
                    source=company_name,
                    value=attribute_value
                ).single()
                if result and result["count(r)"] == 0:  # No relationship found
                    attrb = {'Company': attribute_value}
                    session.run(create_company_query, Company=attribute_value, attributes=attrb)
                    session.run(create_relationship_company_query, source=company_name, target=attribute_value)
            
            attribute = "Headquarters"
            if attribute in company and company[attribute]:
                attribute_value = company[attribute]
                # Check if there is already a relationship for this attribute
                result = session.run(
                    "MATCH (a:Company)-[r:HEADQUARTERS]->(b:City) WHERE a.Company = $source AND b.City = $value RETURN count(r)",
                    source=company_name,
                    value=attribute_value
                ).single()
                if result and result["count(r)"] == 0:  # No relationship found
                    attrb = {'City': attribute_value}
                    session.run(create_city_query, City=attribute_value, attributes=attrb)
                    session.run(create_relationship_city_query, source=company_name, target=attribute_value)

    # Close the Neo4j driver
    driver.close()

# Set Neo4j connection details
uri = "bolt://localhost:7687"
username = "neo4j"
password = "123456789"

# Call the function to import JSON data into Neo4j
import_json_to_neo4j(uri, username, password)
