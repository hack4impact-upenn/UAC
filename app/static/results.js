/***************************************
PAGE INTERACTIVITY
****************************************/

$("#btn_submit_state_ntee").click(function() {
    var state = $("#state_input").val();
    var ntee = $("#ntee_input").val();

    // update values
});

/***************************************
BUILDING BAR GRAPH
****************************************/

/* IMPORTANT: THE DATA */
/* 
    To change the data set, change variable expense_data (below).
    expense_data[0] refers to the current costs being spent in 0-7 categories.
    expense_data[1] refers to the possible costs if user makes switch to UAC, in same 0-7 categories. 
    Both graphs pull from 'expense data' currently for demo, but second graph should pull from data comparing user to other non-profits.
*/

    // var expense_data = [
    //      [50,30,10,40,60,80,30,40,50,60,70,80,90,100,],
    //      [60,50,40,30,20,30,40,50,60,70,80,90,100,110]];

    console.log("HEY");
    console.log(result_data);

    var profndraising = "{{result_data['filing_data']['profndraising']}}";
    var totexpns = "{{result_data['filing_data']['totexpns']}}";

    console.log(profndraising);
    console.log(totexpns);

    var expense_data = [
         [0,0,0,0,0,0,0,0,0,0,0,0,0,0,],
         [0,0,0,0,0,0,0,0,0,0,0,0,0,0]];

    // DATA WITH TOTAL INCLUDED:
    // var expense_data = [
    //     [780,50,40,30,20,10,20,30,40,50,60,70,80,90,100,],
    //     [830,60,50,40,30,20,30,40,50,60,70,80,90,100,110]];

    var labels = ['Management', 'Legal', 'Accounting', 'Lobbying', 'Prof. Fund.', 'Invest. MGMT.', 'Advertising', 'Office Exp.', 'Information Tech.', 'Interest Expense', 'Insurance', 'Empl. Benefits', 'Pension Plan', 'Other'];

    populateForm(); // to fill in cost form with current data 

    var n = 2, // number of layers
        m = 14; // number of samples per layer
    var x;
    var y;
    var rect;
    var yGroupMax;
    var yStackMax;
    var width;
    var height;

    createBarGraph();

    function createBarGraph() {

        updateTotalCost();

        var stack = d3.layout.stack();
        var layers = stack(d3.range(n).map(function(x) {return getData(x); }));
        
        yGroupMax = d3.max(layers, function(layer) { return d3.max(layer, 
            function(d) { return d.y; }); });
        
        yStackMax = d3.max(layers, function(layer) { return d3.max(layer, 
            function(d) { return d.y0 + d.y; }); });

        var margin = {top: 40, right: 10, bottom: 75, left: 10};
        width = 1000 - margin.left - margin.right;
        var diagramWidth = 1000 - margin.left - margin.right - 200;
        height = 600 - margin.top - margin.bottom;

        x = d3.scale.ordinal()
        .domain(d3.range(m))
        .rangeRoundBands([0, diagramWidth], .08);

        y = d3.scale.linear()
        .domain([0, yGroupMax])
        .range([height, 0]);

        // set bar graph colors
        var color = d3.scale.linear().domain([0, n - 1]).range(["#DC4E00", "#89CEDE"]);

        var xAxis = d3.svg.axis()
        .scale(x)
        .tickSize(3)
        .tickPadding(6)
        .ticks([0,1,2,3,4,5,6,7,8,9,10,11,12,13])
        .tickValues([0,1,2,3,4,5,6,7,8,9,10,11,12,13])
        .tickFormat(function(d) { return convertToLabel(d); })
        .orient("bottom");

        var yAxis = d3.svg.axis()
        .scale(y)
        .tickSize(3)
        .ticks(20)
        .tickPadding(0)
        .tickFormat(function(d) {return '$' + d; })
        .orient("left");

        var offset = margin.left + 30; // to move diagram right
        var svg = d3.select("#svg_container").append("svg")
        .attr("width", width + margin.left)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + offset + "," + margin.top + ")");

        var layer = svg.selectAll(".layer")
        .data(layers)
        .enter().append("g")
        .attr("class", "layer")
        .style("fill", function(d, i) { return color(i); });

        rect = layer.selectAll("rect")
        .data(function(d) { return d; })
        .enter().append("rect")
        .attr("x", function(d) { return x(d.x); })
        .attr("y", height)
        .attr("width", x.rangeBand())
        .attr("height", 0)
        .on("mouseover", function(d) {
            layer.selectAll("text")
            .data(function(d) {
                return d;
            })
            .enter()
            .append("text")
            .style("text-anchor","middle")
            //.attr("transform", "rotate(10)")
            .attr("x", function(d) {
                if (d.y0 == 0) return x(d.x) + 10;
                return x(d.x) + 40;
            })
            .attr("y", function(d) {
                return y(d.y) -10;
            })
            .filter(function(e) {
                return e.x == d.x;
            })
            .text(function(d) {
                return '$'+d.y;
            });

        }).on("mouseout",  function(d) { 
            layer.selectAll("text").remove();
        });

        // layer.selectAll("text")
        // .data(function(d) {
        //     return d;
        // })
        // .enter()
        // .append("text")
        // .style("text-anchor","middle")
        // //.attr("transform", "rotate(10)")
        // .attr("x", function(d) {
        //     if (d.y0 == 0) return x(d.x) + 10;
        //     return x(d.x) + 40;
        // })
        // .attr("y", function(d) {
        //     console.log('y = ' + d.y);
        //     return y(d.y) -10;
        // })
        // .text(function(d) {
        //     return '$'+d.y;
        // });

        

        rect.transition()
        .delay(function(d, i) { return i * 10; })
        .attr("y", function(d) { return y(d.y0 + d.y); })
        .attr("height", function(d) { return y(d.y0) - y(d.y0 + d.y); });

        svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .selectAll("text")
        .style("text-anchor","end")
        .attr("transform", function(d) {
            return "rotate(-60)"
        });

        svg.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(0,0)")
        .call(yAxis);

        d3.selectAll("input").on("change", change);

        change();
    }

    function updateTotalCost() {
        var total_cost = 0;
        for (var i = 0; i < m; i++) {
            total_cost += expense_data[0][i];
        }
        $('#total').text(total_cost);
    }

    // m = number of categories
    function convertToLabel(d) {
        if (d >= 0 && d < m) {
            var label = labels[d]
            // if (label.length > 5) {
            //     return label.substring(0,6) + '.';
            // } 
            return label;
            
        } else {
            return 'Not a valid label';
        }
    }

    // to change graph from STACKED to GROUPED bars
    function change() {
        if (this.value === "stacked") transitionStacked();
        else transitionGrouped();
    }

    function transitionGrouped() {
        y.domain([0, yGroupMax]);

        rect.transition()
        .duration(500)
        .delay(function(d, i) { return i * 10; })
        .attr("x", function(d, i, j) { return x(d.x) + x.rangeBand() / n * j; })
        .attr("width", x.rangeBand() / n)
        .transition()
        .attr("y", function(d) { return y(d.y); })
        .attr("height", function(d) { return height - y(d.y); });
    }

    function transitionStacked() {
        y.domain([0, yStackMax]);

        rect.transition()
        .duration(500)
        .delay(function(d, i) { return i * 10; })
        .attr("y", function(d) { return y(d.y0 + d.y); })
        .attr("height", function(d) { return y(d.y0) - y(d.y0 + d.y); })
        .transition()
        .attr("x", function(d) { return x(d.x); })
        .attr("width", x.rangeBand());
    }
    
    /* BAR GRAPH DATA GETTER */
    // n = x axis num categories
    // o = 0.1
    function getData(n) {
        var a = expense_data[n];
        // if (n==0) {
        //     a = [70,40,30,20,50,60,10];
        // } else {
        //     a = [60,10,15,10,25,50,10];
        // }
        var m = a.map(function(d, i) {return {x: i, y: d}; });
        return m;
    }

    function populateForm() {
        $('#management').val(expense_data[0][0]);
        $('#legal').val(expense_data[0][1]);
        $('#accounting').val(expense_data[0][2]);
        $('#lobbying').val(expense_data[0][3]);
        $('#professional_fundraising').val(expense_data[0][4]);
        $('#investment_management').val(expense_data[0][5]);
        $('#advertising').val(expense_data[0][6]);
        $('#office_expenses').val(expense_data[0][7]);
        $('#information_technology').val(expense_data[0][8]);
        $('#interest_expense').val(expense_data[0][9]);
        $('#insurance').val(expense_data[0][10]);
        $('#employee_benefits').val(expense_data[0][11]);
        $('#pension_plan_contributions').val(expense_data[0][12]);
        $('#other').val(expense_data[0][13]);

    }

    $('#costs_form').submit(function() {
        var $inputs = $('#costs_form :input');
        
        var values = [];
        var total = 0;
        $inputs.each(function() {
            var value = parseInt($(this).val());
            if (!isNaN(value)) {
                total = total + value;
                values.push(value);
            }
        });

        expense_data[0] = values;

        $('#svg_container').empty();
        createBarGraph();
        return false;
    });

/***************************************
BUILDING HORIZONTAL SLIDER BARS
****************************************/

    var numBars = 13;
    var gapSize = 70;
    var width = 800;
    var height = numBars*gapSize;


    createHorizontalBars();

    function createHorizontalBars() {
        var rect_container = d3.select("#svg2_container").append("svg")
        .attr("width", width)
        .attr("height",height);

        var rectWidth = width - 100;
        var rectHeight = height/(numBars*2);

        var gradient = rect_container.append("linearGradient")
            .attr('y1', 0)
            .attr('y2', 0)
            .attr('x1', 0)
            .attr('x2', width-100)
            .attr('x3', width-100)
            .attr('id', "gradient")
            .attr('gradientUnits', 'userSpaceOnUse')

        gradient
        .append("stop")
        .attr("offset", "0")
        .attr("stop-color", "#DC4E00")

        gradient
        .append("stop")
        .attr("offset", "0.5")
        .attr("stop-color", "#ffdb33")
        
        gradient
        .append("stop")
        .attr("offset", "1")
        .attr("stop-color", "#31c960")

        for (var i = 0; i < numBars; i++) {
            rect_container.append("rect")
            .attr("x",0)
            .attr("y",i*gapSize)
            .attr("width",rectWidth)
            .attr("height",rectHeight)
            .attr("fill", "url(#gradient)");
        }

        var comparison_data = [
            [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.2],
            [0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.4]];

        for (var i = 0; i < numBars; i++) {
            rect_container.append("line")
            .attr('x1', rectWidth - (comparison_data[0][i] * rectWidth))
            .attr('y1', i*gapSize)
            .attr('x2', rectWidth - (comparison_data[0][i] * rectWidth))
            .attr('y2', i*gapSize + rectHeight)
            .attr('stroke-width',2)
            .attr('stroke','black');

            rect_container.append("line")
            .attr('x1', rectWidth - (comparison_data[1][i] * rectWidth))
            .attr('y1', i*gapSize)
            .attr('x2', rectWidth - (comparison_data[1][i] * rectWidth))
            .attr('y2', i*gapSize + rectHeight)
            .attr('stroke-width',2)
            .attr('stroke','white');
        }
    }
    