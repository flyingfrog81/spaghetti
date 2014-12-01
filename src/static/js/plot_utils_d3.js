(function( $ ) { 
    var AttachedPlot = function(element, opts){
        var jQe = $(element);
        var d3e = d3.select(element);
        var obj = this;
        var o = opts;
        //var id = jQe.attr("id");
        var width, height, plot_width, plot_height;
        var x = d3.scale.linear();
        var y = d3.scale.linear();
        var has_data = false;
        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");
        var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left");
        var svg = d3e.append("svg");
        var g = svg.append("g");
        var line = d3.svg.line()
            .x(function(d, i) { return x(i); })
            .y(function(d)  { return y(d); });
        var plot_xaxis = g.append("g")
            .attr("class" , "x axis")
            .call(xAxis);
        var plot_yaxis = g.append("g")
            .attr("class" , "y axis")
            .call(yAxis);
        var plot = g.append("path")
            .attr("class", "plotline")
            .attr("stroke-width", o.stroke_width)
            .attr("stroke", o.stroke);
        //console.log("added line: " + plot);
        obj.update_dimensions = function(){
            //console.log(id + ".update_dimensions()");
            width = jQe.width();
            height = jQe.height();
            plot_width = width - 2 * o.padding - o.axis_height - o.line_height;
            plot_height = height - 2 * o.padding - o.axis_height - o.line_height;
            x.range([0, plot_width - 1]);
            y.range([plot_height - 1, 0]);
            svg.attr("width", width)
                .attr("height", height);
            g.attr("width", width)
                .attr("height", height);
            plot_xaxis.attr("height", o.axis_height + o.line_height)
                .attr("width", plot_width)
                .attr("transform", "translate(" +
                        (o.padding + o.axis_height + o.line_height) +
                        "," +
                        (o.padding + plot_height) +
                        ")")
                .call(xAxis);
            plot_yaxis.attr("height", plot_height)
                .attr("transform", "translate(" +
                        (o.padding + o.axis_height + o.line_height) +
                        "," +
                        o.padding +
                        ")")
                .call(yAxis);
            plot.attr("width", plot_width)
                .attr("height", plot_height)
                .attr("transform", "translate(" + 
                        (o.padding + o.axis_height + o.line_height) + 
                        "," + 
                        o.padding + 
                        ")");
            if(obj.has_data){
                plot.attr("d", line);
            } //if(obj.has_data){
        }; // var update_dimensions = function(){
        obj.update_dimensions();
        obj.update_data = function(data){
            //console.log(id + ".update_data()");
            //TODO: optionally get min and max values from options
            x.domain([0, data.length - 1]);
            y.domain([0, d3.max(data)]);
            plot_xaxis.call(xAxis);
            plot_yaxis.call(yAxis);
            plot.datum(data)
                .attr("d", line);
            obj.has_data = true;
        }; //obj.update_data = function(data){
        obj.update_options = function(_opts){

        }; //obj.update_options = function(_opts){
    }; //var AttachedPlot = function(element, options){
    $.fn.extend({
        attach_plot : function(options){
            var defaults = {
                padding : 3,
                axis_height : 25,
                line_height : 25,
                stroke_width : "2px",
                stroke : "#152E40",
                ws : null,
            }; // var defaults = {
            var _options = $.extend(defaults, options);
            return this.each(function(){
                var plugin = new AttachedPlot(this, _options);
                plugin.update_dimensions();
                //_options.ws.attach_data_callback(plugin.update_data);
                _options.ws.ondata = plugin.update_data;
                $(window).resize(function(){
                    plugin.update_dimensions();
                }); // window.resize
            }); //this.each(function(){
        }, //attach_plot : function(){
    }); //$.fn.extend({
})(jQuery);
