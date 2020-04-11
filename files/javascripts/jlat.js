function download_csv(csv, filename) {
    var csvFile;
    var downloadLink;
    // CSV FILE
    csvFile = new Blob([csv], {type: "text/csv"});
    // Download link
    downloadLink = document.createElement("a");
    // File name
    downloadLink.download = filename;
    // We have to create a link to the file
    downloadLink.href = window.URL.createObjectURL(csvFile);
    // Make sure that the link is not displayed
    downloadLink.style.display = "none";
    // Add the link to your DOM
    document.body.appendChild(downloadLink);
    // Lanzamos
    downloadLink.click();
}

function export_table_to_csv(id, filename) {
	var csv = [];
    var rows = document.getElementById(id).querySelectorAll(".siimple-table-row:not(.hidden)");
    //header
    var row = [], cols = rows[0].querySelectorAll(".siimple-table-cell");
    for (var j = 0; j < cols.length; j++) 
        row.push(cols[j].innerText.toLowerCase());
    csv.push(row.join(";"));
    //body	
    for (var i = 1; i < rows.length; i++) {
		var row = [], cols = rows[i].querySelectorAll(".siimple-table-cell");
        for (var j = 0; j < cols.length; j++) 
            row.push(cols[j].innerText);
		csv.push(row.join(";"));		
	}
    // Download CSV
    download_csv(csv.join("\n"), filename);
}

function searchAdvanced(idinput, idtable) {
    var searchvalue = document.getElementById(idinput).value;
    var rows = document.getElementById(idtable).querySelectorAll(".siimple-table-body .siimple-table-row");
    if (searchvalue.indexOf(':') !== -1) {
        key = searchvalue.split(':')[0]
        value = searchvalue.split(':')[1]
        pos=0;
        var thead = document.getElementById(idtable).querySelectorAll(".siimple-table-header .siimple-table-cell");
        for (var i = 0; i < thead.length; i++) {
            if (thead[i].textContent == key){
                pos = i;
            }
        }
        for (var i = 0; i < rows.length; i++) {
            if (rows[i].querySelectorAll(".siimple-table-cell")[pos].textContent.includes(value)) {
                rows[i].classList.remove("hidden")
            } else {
                rows[i].classList.add("hidden")
            }	
        }
    } else {
        for (var i = 0; i < rows.length; i++) {
            var cols = rows[i].querySelectorAll(".siimple-table-cell");
            var found = false;
            for (var j = 0; j < cols.length; j++) {
                if (cols[j].textContent.includes(searchvalue)) {
                    found = true
                }
            };
            if (found) {
                rows[i].classList.remove("hidden")
            } else {
                rows[i].classList.add("hidden")
            }	
        }
    }
}

if (document.getElementById("search")) {
document.getElementById("search").addEventListener("input", function(){searchAdvanced("search", "table")});
};

function view_wait() {
    document.getElementById("nowait").classList.add("hidden");
    document.getElementById("wait").classList.remove("hidden");
}


// ***************************************************** //
//                  specific jalt                        //