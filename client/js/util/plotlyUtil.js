angular.module('ERAS').factory('PlotlyUtil', [function() {

	var _render  = function(containerId, data, layout, config){

	    var container = document.getElementById(containerId);
		//cleaning container
        while(container.firstChild) {
            container.removeChild(container.firstChild);
        }

        var gd3 = Plotly.d3.select('#'+containerId).append('div').style({
                width: '100%',
                height: '100%'
            });

        var gd = gd3.node();

        //Plotly.plot(gd, data, layout);

        if(window.attachEvent) {
            window.attachEvent('onresize', function() {
                Plotly.Plots.resize(gd);
            });
        }else if(window.addEventListener) {
            window.addEventListener('resize', function() {
                Plotly.Plots.resize(gd);
            }, true);
        }

        Plotly.plot(gd, data, layout, config).then(function() {
            window.requestAnimationFrame(function() {
                window.requestAnimationFrame(function() {
                    //Plotly.Plots.resize(gd);
                    angular.element(window).resize();
                });
            });
        });

        //angular.element(window).resize();
	}

	var _renderBarChart  = function(containerId, series, config){
	    var layout = {
            barmode: config.barmode ? config.barmode : 'overlay' //'stack', 'overlay', group
        }
        if(config){
            if(config.xaxis){
                layout.xaxis = config.xaxis;
            }
            if(config.yaxis){
                layout.yaxis = config.yaxis;
            }
            if(config.margin){
                layout.margin = config.margin;
            }
        }

        var data = [];

        series.forEach(function(value){

            data_to_push = {
                x: value.x,
                y: value.y,
	            name: value.name,
                orientation: config.orientation ? config.orientation : 'v', // 'h', 'v'
                type: 'bar'
            }

            if(value.marker){
                data_to_push['marker'] = value.marker;
            }

            data.push(data_to_push);

        });

        _render(containerId, data, layout)
	}

	var _renderScattedChart  = function(containerId, series, config, hasLine){

        var layout = {}

        if(config){
            if(config.xaxis){
                layout.xaxis = config.xaxis;
            }
            if(config.yaxis){
                layout.yaxis = config.yaxis;
            }
            if(config.margin){
                layout.margin = config.margin;
            }
        }

        var data = [];
        var dataGroupByName = [];

        series.forEach(function(value){

            if(!dataGroupByName[value.name]){
                dataGroupByName[value.name] = {
                    x: [],
                    y: [],
                    text: [],
                    name: value.name,
                    mode: hasLine ? 'lines+markers' : 'markers',
                    //type: 'scatter',
                    line: {
                        width: 1
                    },
                    marker: {
                        size: 5
                    }
                };
                data.push(dataGroupByName[value.name]);
            }

            dataGroupByName[value.name].x.push(value.x);
            dataGroupByName[value.name].y.push(value.y);
            dataGroupByName[value.name].text.push(value.text);

            /*data_to_push = {
                x: value.x,
                y: value.y,
	            name: value.name,
	            mode: 'markers',
                type: 'scatter'
            }*/

            /*if(value.marker){
                data_to_push['marker'] = value.marker;
            }*/

        });

        _render(containerId, data, layout)
	}

	var _renderPieChart  = function(containerId, data, config){

	    data.type = 'pie';

        var layout = {
            font: {weight:'bold'}
        }
        if(config){
            if(config.showlegend != undefined){
                layout.showlegend = config.showlegend;
            }
            if(config.margin){
                layout.margin = config.margin;
            }
        }

        _render(containerId, [data], layout);

	}

	var _renderHeatMapChart  = function(containerId, data){

        var layout = {
            annotations: [],
            xaxis: {
                ticks: '',
                side: 'top',
                tickangle: 90
            },
            yaxis: {
                ticks: '',
                ticksuffix: ' ',
                autorange: 'reversed'
            },
            margin: {
                r: 20, t: 120, b: 10, l:120
            }
        };

        var colorscaleValue = [
            [0, '#ffffff'],
            [0.20, '#f7f7f7'],
            [0.40, '#dfe3ee'],
            [0.80, '#8b9dc3'],
            [1, '#3b5998']
        ];

        for ( var i = 0; i < data.y.length; i++ ) {
            for ( var j = 0; j < data.x.length; j++ ) {
                var currentValue = data.z[i][j];
                if (currentValue >= 0.8) {
                    var textColor = 'white';
                }else{
                    var textColor = 'black';
                }
                var result = {
                    xref: 'x1',
                    yref: 'y1',
                    x: data.x[j],
                    y: data.y[i],
                    text: currentValue == undefined ? '' : currentValue,
                    font: {
                        family: 'Arial',
                        size: 12,
                        color: 'rgb(50, 171, 96)'
                    },
                    showarrow: false,
                    font: {
                        color: textColor
                    }
                };
                layout.annotations.push(result);
            }
        }

        var data = [{
            x: data.x,
            y: data.y,
            z: data.z,
            type: 'heatmap',
            colorscale: colorscaleValue,
            zmin:0,
            zmax:1,
            showscale: false
        }];

        _render(containerId, data, layout);

	}

    return {
    	render : _render,
    	renderBarChart : _renderBarChart,
    	renderScattedChart : _renderScattedChart,
    	renderPieChart : _renderPieChart,
    	renderHeatMapChart : _renderHeatMapChart
    }

}]);