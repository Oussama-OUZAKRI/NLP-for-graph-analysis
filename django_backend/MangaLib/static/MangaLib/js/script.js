// Récupérer l'élément conteneur du graphe dans le DOM
var graphContainer = document.getElementById('graphContainer');
var nodePropertiesDiv = document.getElementById('nodeProperties');

// Vérifier que les éléments existent
if (!graphContainer) {
    console.error('graphContainer not found');
} else {
    console.log('graphContainer found');
}

if (!nodePropertiesDiv) {
    console.error('nodePropertiesDiv not found');
} else {
    console.log('nodePropertiesDiv found');
}

// Définir les options de configuration pour le graphe Cytoscape
var cyOptions = {
    container: graphContainer,
    elements: {
    },
    style: [
        {
            selector: 'node',
            style: {
                'width': '50px',
                'height': '50px',
                'background-color': '#2D8BA8',
                'border-color': '#4E8397',
                'border-width': '2px',
                'color': '#FFFFFF',
                'padding': '15px',
                'font-size': '10px',
                'label': 'data(label)',
                'text-valign': 'center',
                'text-halign': 'center',
                'text-wrap': 'wrap',
                'transition-property': 'background-color, border-color, width, height',
                'transition-duration': '0.5s'
            }
        },
        {
            selector: 'node:selected',
            style: {
                'background-color': '#DAA520',
                'border-color': '#FFD700',
                'width': '60px',
                'height': '60px'
            }
        },
        {
            selector: 'edge',
            style: {
                'line-color': '#4E8397',
                'width': '1px',
                'font-size': '8px',
                'padding': '3px',
                'color': '#000000',
                'text-opacity': '1',
                'target-arrow-color': '#4E8397',
                'target-arrow-shape': 'triangle',
                'label': 'data(type)',
                'text-rotation': 'autorotate',
                'text-margin-y': -10
            }
        }
    ],    
    layout: {
        name: 'cose', // Utilisation du layout 'cose' pour une disposition automatique des noeuds
        animate: 'end',
        animationEasing: 'ease-out',
        animationDuration: 1000,
        idealEdgeLength: 100, // Longueur idéale des arêtes
        nodeOverlap: 20, // Chevauchement des noeuds
        refresh: 20, // Rafraîchissement du layout
        fit: true, // Adapter le graphe au conteneur
        padding: 30, // Marge intérieure du conteneur
        randomize: true, // Désactiver la randomisation de la disposition des noeuds
        componentSpacing: 100, // Espacement entre les composants du graphe
        nodeRepulsion: 400000, // Répulsion entre les noeuds
        edgeElasticity: 100, // Elasticité des arêtes
        nestingFactor: 5, // Facteur de nidification
        gravity: 80, // Gravité
        numIter: 1000, // Nombre d'itérations
        initialTemp: 200, // Température initiale
        coolingFactor: 0.95, // Facteur de refroidissement
        minTemp: 1.0 // Température minimale
    }    
};


function rechercherDonneesDansNeo4j() {
    var inputValue = document.getElementById("searchInput").value;
    console.log(inputValue);
    
    if (graphContainer) {
        graphContainer.classList.add('hidden');
        console.log('graphContainer hidden');
    }

    if (nodePropertiesDiv) {
        nodePropertiesDiv.classList.add('hidden');
        console.log('nodePropertiesDiv hidden');
    }
    
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/manga/search?input_value=" + encodeURIComponent(inputValue), true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                var response = JSON.parse(xhr.responseText);
                console.log(response);
                if (response['message'] || response['nodes'].length == 0) {
                    // Si la réponse ne contient pas de nœuds, afficher "Aucun résultat trouvé !"
                    document.getElementById('graphContainer').innerHTML = '<p>Aucun résultat trouvé !</p>';
                    graphContainer.classList.remove('hidden');
                    console.log('graphContainer shown');
                } else {
                    var formattedNodes = [];
                    if (response['nodes']) {
                        response['nodes'].forEach(function (node) {
                            formattedNodes.push({
                                data: {
                                    id: node['id'],
                                    label: node['label'],
                                    properties: node['properties']
                                }
                            });
                        });
                    }
                    console.log(formattedNodes)
                    var formattedEdges = [];
                    if (response['edges']) {
                        response['edges'].forEach(function (edge) {
                            formattedEdges.push({
                                data: {
                                    id: edge['id'],
                                    source: edge['source'],
                                    target: edge['target'],
                                    type: edge['type']
                                }
                            });
                        });
                    }
                    console.log(formattedEdges)
                    cyOptions['elements'] = {
                        nodes: formattedNodes,
                        edges: formattedEdges
                    }

                    // Créer une instance de Cytoscape avec les options définies
                    var cy = window.cytoscape(cyOptions);
                    graphContainer.classList.remove('hidden');
                    console.log('graphContainer shown');

                    // Ajoutez un gestionnaire d'événements pour les clics sur les nœuds
                    cy.on('tap', 'node', function (evt) {
                        var node = evt.target;
                        var properties = node.data('properties');
                        var nodePropertiesDiv = document.getElementById('nodeProperties');
                        var propertiesHTML = '<h3>Node Properties</h3><ul>';
                        for (var key in properties) {
                            propertiesHTML += '<li><strong>' + key + '</strong>: ' + properties[key] + '</li>';
                        }
                        propertiesHTML += '</ul>';
                        nodePropertiesDiv.innerHTML = propertiesHTML;
                        nodePropertiesDiv.classList.remove('hidden');
                        console.log('nodePropertiesDiv shown');
                    });

                    // Ajoutez un gestionnaire d'événements pour masquer les propriétés des nœuds lorsqu'on clique en dehors d'un nœud
                    cy.on('tap', function (evt) {
                        if (evt.target === cy) {
                            nodePropertiesDiv.classList.add('hidden');
                            console.log('nodePropertiesDiv shown');
                        }
                    });

                    // Gestionnaires d'événements pour le survol des nœuds
                    cy.on('mouseover', 'node', function(evt) {
                        var node = evt.target;
                        node.style({
                            'background-color': '#FFD700',
                            'border-color': '#DAA520',
                            'width': '55px',
                            'height': '55px'
                        });
                    });

                    cy.on('mouseout', 'node', function(evt) {
                        var node = evt.target;
                        node.style({
                            'background-color': '#2D8BA8',
                            'border-color': '#4E8397',
                            'width': '50px',
                            'height': '50px'
                        });
                    });

                    // Ajouter une animation pour les nœuds lors de leur ajout
                    cy.elements().animate({
                        style: { 'opacity': 1 },
                        duration: 1000
                    });
                }
            } else {
                // En cas d'erreur, afficher un message d'erreur dans le conteneur du graphe
                document.getElementById('graphContainer').innerHTML = '<p>Une erreur s\'est produite lors de la récupération des données.</p>';
                graphContainer.classList.remove('hidden');
                console.log('graphContainer shown');
            }
        }
    };
    xhr.send();
}
