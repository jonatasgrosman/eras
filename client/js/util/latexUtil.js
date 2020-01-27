angular.module('ERAS').factory('LatexUtil', [function() {

    var _downloadTable = function(tableId, tableCaption, fileName) {

        var escape_special_chars = function(str){
            //return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
            return str.replace(/[&%$#{}~^\\]/g, "\\$&");  //'& % $ # _ { } ~ ^ \'
        };

        var table = document.getElementById(tableId);

        var header = [];
        var body = [];
        var footer = [];

        for (var i = 0, row; row = table.rows[i]; i++) {

            if(row.offsetParent){ //is visible
                var newRow = [];
                var isThRow = false;

                for (var j = 0, col; col = row.cells[j]; j++) {
                    isThRow = col.localName == 'th';
                    newRow.push(escape_special_chars(col.innerText));
                }

                if(isThRow && body.length == 0){
                    header.push(newRow);
                }else if(isThRow){
                    footer.push(newRow);
                }else{
                    body.push(newRow);
                }
            }

        }

        /*
        \begin{table}[h!]
          \centering
          \caption{Caption for the table.}
          \label{tab:table1}
          \begin{tabular}{ccc}
            \toprule
            Some & actual & content\\
            \midrule
            prettifies & the & content\\
            as & well & as\\
            using & the & booktabs package\\
            \bottomrule
         using & the & booktabs package\\
          \end{tabular}
        \end{table}
        */

        var latexTable = '% -*- coding: utf-8; -*-\n';
        latexTable += '\\begin{table}[h!]\n';
        latexTable += '\\centering\n';
        latexTable += '\\caption{'+tableCaption+'}\n';
        latexTable += '\\label{tab:tableX}\n';
        latexTable += '\\resizebox{\\textwidth}{!}{%\n'; // needs \usepackage{graphicx}
        latexTable += '\\begin{tabular}{'+Array(header[0].length+1).join("c")+'}\n';
        latexTable += '\\toprule\n';
        header.forEach(function(row){
            row = row.map(function(cell){return '\\textbf{'+cell+'}'});
            latexTable += row.join(' & ') + '\\\\\n'
        });
        latexTable += '\\midrule\n';
        body.forEach(function(row){
            latexTable += row.join(' & ') + '\\\\\n'
        });
        latexTable += '\\bottomrule\n';
        footer.forEach(function(row){
            row = row.map(function(cell){return '\\textbf{'+cell+'}'});
            latexTable += row.join(' & ') + '\\\\\n'
        });
        latexTable += '\\end{tabular}}\n';
        latexTable += '\\end{table}\n';

        console.log(header);
        console.log(body);
        console.log(footer);

        var blob = new Blob([latexTable], {
            type: "text/plain;charset=utf-8;",
        });

        if(!fileName){
            fileName = 'table.txt'
        }

        saveAs(blob, fileName);
    };

    return {
        downloadTable : _downloadTable
    }

}]);
