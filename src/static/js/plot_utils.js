(function( $ ) { 
    $.fn.extend({
        attach_plot : function(options){
            var defaults = {
                padding : 3,
                axis_height : 25,
                line_height : 25,
                ws = null;
            };
            var options = $.extend(defaults, options);
            return this.each(function(){
                var o = options;
                var obj = $(this);
                var width = obj.width();
                var height = obj.height();
                var plot_width = width - 2 * o.padding - o.axis_height - o.line_height;
                var plot_height = heigth - 2 * o.padding - o.axis_height - o.line_height;
                var x = d3.scale.linear()
                    .range([0, plot_width - 1]);
                var y = d3.scale.linear()
                    .range([plot_heigth - 1, 0]);
                var xAxis = d3.svg.axis()
                    .scale(x)
                    .orient("bottom");
                var yAxis = d3.svg.axis()
                    .scale(y)
                    .orient("left");
                var svg = obj.append("svg")
                    .attr("width", width)
                    .attr("height", height)
                    .append("g");
                var line = d3.svg.line()
                    .x(function(d, i) { return x(i); })
                    .y(function(d)  { return y(d); });
                var first_data = true;
                o.ws.ondata = function(data){
                    x.domain([0, data.length - 1]);
                    y.domain([0, d3.max(data)]);
                    if(first_data){
                        var plot_xaxis = svg.append("g")
                            .attr("class", "x axis")
                            .attr("height", o.axis_height + o.line_height)
                            .attr("width", plot_width)
                            .attr("transform", "translate(" +
                                    (o.padding + o.axis_height + o.line_height) +
                                    "," +
                                    (o.padding + plot_height) +
                                    ")")
                            .call(xAxis);
                        var plot_yaxis = svg.append("g")
                            .attr("class", "y axis")
                            .attr("height", plot_height)
                            .attr("width", o.axis_height + o.line_height)
                            .attr("transform", "translate(" +
                                    (o.padding + o.axis_height + o.line_height) +
                                    "," +
                                    o.padding +
                                    ")")
                            .call(yAxis);
                        var plot = svg.append("path")
                            .attr("class", "plotline")
                            .datum(data)
                            .attr("width", plot_width)
                            .attr("height", plot_height)
                            .attr("transform", "translate(" + 
                                    (o.padding + o.axis_height + o.line_height) + 
                                    "," + 
                                    o.padding + 
                                    ")")
                            .attr("d", line);
                        first_data = false;
                    }else{ //not first_data
                        svg.select(".plotline")
                            .datum(data)
                            .attr("d", line);
                    }
                }; //o.ws.ondata
            });
        },
    });
})(jQuery);
