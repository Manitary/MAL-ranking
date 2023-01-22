var dataSelectorValues = [0, 1000, 5000, 10000, 12000];
var dataFiles = [
    "webpage-data/50027_0.json",
    "webpage-data/50027_1000.json",
    "webpage-data/50027_5000.json",
    "webpage-data/50027_10000.json",
    "webpage-data/50027_12000.json",
];
var anime = {};
var datasets = [];

function sliderTextUpdate(selectorName, selectorTextName, arrayValues = null) {
    var slider = document.getElementById(selectorName);
    var output = document.getElementById(selectorTextName);    
    slider.oninput = function () {
        if (arrayValues) {
            output.innerHTML = arrayValues[this.value]
        }
        else {
            output.innerHTML = this.value;
        }
    };
    if (arrayValues == null) output.innerHTML = slider.value;
    else output.innerHTML = dataSelectorValues[slider.value];
};

function fillTable(elementID, dataSelectorID, cutoffSelectorID) {
    var table = document.getElementById(elementID);
    var idx = document.getElementById(dataSelectorID).value;
    var cutoff = document.getElementById(cutoffSelectorID).value;
    table.innerHTML = '<tr id="tableHeaders">' +
        '<th>Rank</th>' +
        '<th>MAL Rank</th>' + 
        '<th>MAL Score</th>' +
        '<th>Parameter</th>' +
        '<th>Title</>' +
        '<th>English title</>' +
        '</tr>';
    var i = 0;
    for ([index, entry] of datasets[idx].entries()) {
        if (entry['num_lists'] > cutoff) {
            i += 1;
            var id = entry['mal_ID'];
            var tr = document.createElement('tr');
            tr.innerHTML = '<td>' + i + '</td>' +
                '<td>' + anime[id]['rank'] + '</td>' +
                '<td>' + (anime[id]['score'] || '-') + '</td>' +
                '<td>' + entry['parameter'] + '</td>' +
                '<td>' + anime[id]['title'] + '</td>' +
                '<td>' + (anime[id]['title_en'] || '-') + '</td>';
            table.appendChild(tr);
        };
    };
};

function fetchData(index) {
    if (datasets[index] == null) {
        fetch(dataFiles[index])
            .then(response => response.json())
            .then(data => {
                datasets[index] = data;
            })
            .then(() => {
                if (Object.keys(anime).length == 0) {
                    fetch("webpage-data/anime.json")
                        .then(response => response.json())
                        .then(data => { anime = data })
                        .then(() => fillTable("animeTable", "dataSelector", "cutoffSelector"))
                        .catch(e => console.error(e));
                }
                else fillTable("animeTable", "dataSelector", "cutoffSelector")
            })
            .catch(e => console.error(e));
    }
    else fillTable("animeTable", "dataSelector", "cutoffSelector");
};

function sliderSelectData(selectorName) {
    var slider = document.getElementById(selectorName);
    slider.onchange = () => fetchData(slider.value);
};

function sliderFilter(filterName, selectorName) {
    var slider = document.getElementById(filterName);
    var selector = document.getElementById(selectorName);
    slider.onchange = () => fetchData(selector.value);
};
