from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
from neo4j import GraphDatabase
import spacy

def index(request):
    context = {"message" : "Application WEB"}
    template = loader.get_template("MangaLib/index.html")
    return HttpResponse(template.render(context, request))

class Neo4jService:
    def __init__(self, uri, user, pwd):
        self._driver = GraphDatabase.driver(uri, auth=(user, pwd))

    def close(self):
        self._driver.close()

    def run_query(self, query, params=None):
        with self._driver.session() as session:
            result = session.run(query, params)
            return [record for record in result]

def search_bar(request):
    # Charger le modèle SpaCy pour l'anglais
    nlp = spacy.load("en_core_web_lg")

    neo4j_uri = f'bolt://{settings.NEO4J_HOST}:{settings.NEO4J_PORT}'
    neo4j_username = settings.NEO4J_USERNAME
    neo4j_password = settings.NEO4J_PASSWORD
    neo4j = Neo4jService(neo4j_uri, neo4j_username, neo4j_password)

    # Récupérez la valeur saisie dans l'input
    input_value = request.GET.get('input_value', '')

    # Utiliser SpaCy pour prétraiter le texte et extraire les entités nommées
    doc = nlp(input_value)
    print(doc)
    entities = {
        "PERSON": [],   # Personnes
        "GPE": [],      # Lieux (Pays, Villes, États)
        "ORG": []       # Organisations/Entreprises
    }
    
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
    print(entities)
    # Construire la requête Neo4j en fonction des entités extraites
    query = ""
    for label, values in entities.items():
        if values:
            if query:
                query += " OR "
            if label == "PERSON" :
                query += "MATCH (n:Person)-[r]-(related) WHERE "
            elif label == "GPE" :
                query += "MATCH (n:City)-[r]-(related) WHERE "
            elif label == "ORG" :
                query += "MATCH (n:Company)-[r]-(related) WHERE "
            
            for i, value in enumerate(values):
                if i > 0:
                    query += " OR "
                if label == "PERSON" :
                    query += f"n.name CONTAINS '{value}'"
                elif label == "GPE" :
                    query += f"n.City CONTAINS '{value}'"
                elif label == "ORG" :
                    query += f"n.Company CONTAINS '{value}'"
    if query:
        query += " RETURN n, r, related"
    else : 
        return JsonResponse({'message' : 'Aucun résultat trouvé !'})
    print(query)

    # Exemple de requête à Neo4j en fonction de la valeur saisie
    # query = f"MATCH (n {{Company: '{input_value}'}})-[r]->(related) RETURN n, r, related"
    
    result = neo4j.run_query(query)

    nodes = []
    edges = []

    # Parcourir les résultats de la requête Neo4j
    for record in result:
        for i in range(len(record)) :
            if i==0 or i == 2 :
                # Vérifier le type du nœud
                elt = record[i]
                node_type = list(elt.labels)[0]
                
                redondant = {'id': elt.element_id, 'label': elt.get('Company'), 'properties' : elt._properties}
                # Traiter les nœuds en fonction de leur type
                if node_type == 'Company' and not redondant in nodes:
                    # Ajouter un nœud de type Company
                    print('Company : '+elt.get('Company'))
                    nodes.append({'id': elt.element_id, 'label': elt.get('Company'), 'properties' : elt._properties})
                elif node_type == 'Person':
                    # Ajouter un nœud de type Person
                    print('name : '+elt.get('name'))
                    nodes.append({'id': elt.element_id, 'label': elt.get('name'), 'properties' : elt._properties})
                elif node_type == 'City':
                    # Ajouter un nœud de type City
                    print('City : '+elt.get('City'))
                    nodes.append({'id': elt.element_id, 'label': elt.get('City'), 'properties' : elt._properties})
            if i == 1 :
                edges.append({'id': record[i].element_id, 'source': record[i].start_node.element_id, 'target': record[i].end_node.element_id,  'type': record[i].type})
        
    neo4j.close()
    
    # Renvoyer les données du graphe (ou toute autre donnée que vous voulez renvoyer)
    return JsonResponse({'nodes': nodes, 'edges': edges})