document.addEventListener('DOMContentLoaded', function(){
    var cyData = document.getElementById('cy').getAttribute('data-graph');
    var parsedCyData = JSON.parse(cyData);

    var cy = cytoscape({
        container: document.getElementById('cy'),

        elements: parsedCyData,
        
        style: [
            {
                selector: 'node',
                style: {
                    'background-color': '#666',
                    'label': 'data(label)'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 3,
                    'line-color': '#ccc'
                }
            }
        ],
        
        layout: {
            name: 'circle'
        }
    });
});
