const NUM_OF_EXPENSE_CATEGORIES = 14;

$(document).ready(function() {

    var savingsData; 

    updateTotalExpenseAndValidateFields();

    $('.form-control').change(function() {
        updateTotalExpenseAndValidateFields();
    });

    /*
    $("#btn_submit_state_ntee").click(function() {
        var state = $("#state_input").val();
        var ntee = $("#ntee_input").val();
        // update values
    });*/

    $("#submit_button_calculate").click(function(event){
        event.preventDefault();
        // first, validate
        // field_names has all field names except total_expense - no need to validate it
        var field_names = ['#pension_plan_contributions', '#othremplyeebene',
            '#feesforsrvcmgmt', '#legalfees', '#accountingfees',
            '#feesforsrvclobby', '#profndraising', '#feesforsrvcinvstmgmt',
            '#feesforsrvcothr', '#advrtpromo', '#officexpns', '#infotech',
            '#interestamt', '#insurance', '#total_revenue'];

        for (var i=0; i < field_names.length; i++) {

            if (  !isValidInt( $(field_names[i]).val() )  ) {
                $(document).scrollTop( $(field_names[i]).parent().offset().top - 60 );
                return;
            }
        }
                
        var expense_data = {
            pension_plan_contributions:$('#pension_plan_contributions').val(),
            othremplyeebene:$('#othremplyeebene').val(),
            feesforsrvcmgmt:$('#feesforsrvcmgmt').val(),
            legalfees:$('#legalfees').val(),
            accountingfees:$('#accountingfees').val(),
            feesforsrvclobby:$('#feesforsrvclobby').val(),
            profndraising:$('#profndraising').val(),
            feesforsrvcinvstmgmt:$('#feesforsrvcinvstmgmt').val(),
            feesforsrvcothr:$('#feesforsrvcothr').val(),
            advrtpromo:$('#advrtpromo').val(),
            officexpns:$('#officexpns').val(),
            infotech:$('#infotech').val(),
            interestamt:$('#interestamt').val(),
            insurance:$('#insurance').val(),
            // don't forget to convert the dollar to proper number
            total_expense: $('#total_expense').html().replace(/[^0-9\.]+/g,""),
            total_revenue:$('#total_revenue').val(),
            state_id:$('#state_select').val(),
            ntee_id:$('#ntee_select').val(),
            revenue_id:$('#revenue_select').val()
        };
        console.log('insurance: ' + $('#insurance').val());
        console.log('total expense: ' + expense_data);
        console.log(expense_data);
        
        $.post('/calculate',
            expense_data,
            function(data, status) {
                
                /* 
                 * Calculate the total savings amount.
                 * The formula provided by UAC is used.
                 */
                var savings = (  parseInt( $('#feesforsrvcmgmt').val() ) +
                              parseInt( $('#accountingfees').val() ) +
                              parseInt( $('#officexpns').val() ) +
                              parseInt( $('#infotech').val() ) +
                              parseInt( $('#othremplyeebene').val() )  ) * 0.15 +
                              
                              (  parseInt( $('#profndraising').val() ) +
                              parseInt( $('#feesforsrvcinvstmgmt').val() ) +
                              parseInt( $('#feesforsrvcothr').val() ) +
                              parseInt( $('#advrtpromo').val() )  ) * 0.1 + 

                              parseInt( $('#interestamt').val() ) + 
                              
                              Math.max(0, parseInt( $('#pension_plan_contributions').val() ) - 2260) +

                              Math.max(0, parseInt( $('#insurance').val() ) - parseInt( $('#total_revenue').val() )*0.01 );

                $('#total-savings-amount').html('$' + (savings.toFixed(0) + '').replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,") + '.');
                savingsData = calculateSavingsData(expense_data);
                createBarGraph(savingsData);
                

                console.log(data);

                if (data.no_such_bucket) {
                    alert('We do not have data for this peer group at the moment. Please try a different selection. Sorry!');
                    return;
                }

                $('#total-overhead-rate').html(parseFloat(data.this_nonprofit_expense_percent.totalefficiency).toFixed(2) + '%.');
                $('#total-efficiency-ranking').html(((data.this_nonprofit_rankings.totalefficiency)*100).toFixed(2) + '%');
                var inputData = data;

                // The Google chart for comparison visualization
                function drawCompareChart() {
                    // checking if the data made it here
                    console.log(inputData);

                    // initialize the datatable
                    var data = new google.visualization.DataTable();

                    // label the columns (X stands for the x-axis labels)
                    var labels = ['X', 'Other employee benefits', 'Management',
                                  'Legal', 'Accounting', 'Lobbying',
                                  'Professional fundraising services', 'Investment management fees', 'Other',
                                  'Advertising and promotion', 'Office expenses',
                                  'Information technology', 'Interest', 'Insurance', 'Total efficiency'];
                    for (var i=0; i < labels.length; i++) {
                        data.addColumn('number', labels[i]);
                        data.addColumn({type:'string', role:'style'});
                    }

                    // re-format the input data:
                    // first, insert other nonprofits' data
                    inputData.other_nonprofits_expense_percent['percentiles'] = $.map(inputData.other_nonprofits_rankings, function(elem){
                        return (elem*100).toFixed(2);
                    });
                    var field_names = [ 'percentiles', 'othremplyeebene',
                                        'feesforsrvcmgmt', 'legalfees', 'accountingfees',
                                        'feesforsrvclobby', 'profndraising', 'feesforsrvcinvstmgmt',
                                        'feesforsrvcothr', 'advrtpromo', 'officexpns', 'infotech',
                                        'interestamt', 'insurance', 'totalefficiency'];

                    var allRows = [];
                    for (var i=0; i < inputData.other_nonprofits_rankings.length; i++) {
                        var row = [];
                        
                        for (var j=0; j < field_names.length; j++) {
                            row.push( parseFloat(inputData.other_nonprofits_expense_percent[ field_names[j] ][i]) );
                            row.push(null);
                        }
                        allRows.push(row);
                    }

                    // now, insert the data for the current nonprofit:
                    for (var i=1; i < field_names.length; i++) {
                        var row = [parseFloat((parseFloat(inputData.this_nonprofit_rankings[ field_names[i] ])*100).toFixed(2)), null];

                        for (var j=0; j < 28; j++) {
                            row.push(null);
                        }
                        row[i*2] = parseFloat(parseFloat(inputData.this_nonprofit_expense_percent[ field_names[i] ]).toFixed(2));
                        row[i*2 + 1] = 'point { size: 10';
                        allRows.push(row);
                    }

                    console.log(allRows);
                    // finally, add all data to the dataTable
                      data.addRows(allRows);

                      var options = {
                        hAxis: {
                          title: 'Percentile'
                        },
                        vAxis: {
                          title: '% of the total revenue',
                          logScale: true
                        },
                        series: {
                          1: {curveType: 'function'}
                        },
                        height: 550,
                        pointSize: 5,
                        backgroundColor: '#E9FCD1'
                      };

                      var chart = new google.visualization.LineChart(document.getElementById('chart_div'));

                      // format the data for tooltips
                      var formatter = new google.visualization.NumberFormat(
                          {suffix: '% of the total revenue'});
                      
                      for (var i=1; i < 15; i++) {
                          formatter.format(data, i*2);
                      }

                      chart.draw(data, options);
                }
                google.load('visualization', '1', {packages: ['corechart', 'line'], callback: drawCompareChart});
                $(document).scrollTop( $('#compare').offset().top );
                /*
                console.log('make horizontal bars');
                var numBars = 14;
                var gapSize = 70;
                var width = 800;
                var height = numBars*gapSize;
                var thisNonprofitRankings = $.map(data.this_nonprofit_rankings, function(value, index) {
                    return value;
                });
                createHorizontalBars(thisNonprofitRankings, numBars, gapSize, width, height);*/
                
                
            });
        
    }); // $("#submit_button_calculate").click(function(event){

/***************************************
BUILDING BAR GRAPH
****************************************/

    // auto-populates bar graph with 0-values if none have been submitted yet
    if(typeof savingsData === 'undefined'){
        var initial_data = [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ];
        createBarGraph(initial_data);
    } else {
        createBarGraph(savingsData);
    }  

    var sample_data = [
            [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.2], //lines:percentage values
            [0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.4],
            [0.7,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.8,0.7,0.6,0.5,0.4,0.3],
            [0.4,0.5,0.6,0.7,0.8,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.4,0.2]];
    createHorizontalBars(sample_data);


    /*** FRONT END ***/
    
    // jQuery for page scrolling feature - requires jQuery Easing plugin
    $(function() {
        $('a.page-scroll').bind('click', function(event) {
            var $anchor = $(this);
            $('html, body').stop().animate({
                scrollTop: $($anchor.attr('href')).offset().top
            }, 1500, 'easeInOutExpo');
            event.preventDefault();
        });
    });

    // Highlight the top nav as scrolling occurs
    $('body').scrollspy({
        target: '.navbar-fixed-top'
    })

    // Closes the Responsive Menu on Menu Item Click
    $('.navbar-collapse ul li a').click(function() {
        $('.navbar-toggle:visible').click();
    });

}); //$(document).ready(function()

/*
    Input: Current expense data (JSON object) 
    Output: Array formatted for D3 use, has current expense data and projected expense data with UAC
*/
function calculateSavingsData(input_expense_data) {
    // transform data from JSON obj to array
    var current_expenses = $.map(input_expense_data, function(value, index) {
        return parseInt(value);
     });
    // update values to reflect UAC savings
    input_expense_data['feesforsrvcmgmt'] = 0.85 * input_expense_data['feesforsrvcmgmt'];
    input_expense_data['accountingfees'] = 0.85 * input_expense_data['accountingfees'];
    input_expense_data['profndraising'] = 0.9 * input_expense_data['profndraising'];
    input_expense_data['feesforsrvcinvstmgmt'] = 0.9 * input_expense_data['feesforsrvcinvstmgmt'];
    input_expense_data['feesforsrvcothr'] = 0.9 * input_expense_data['feesforsrvcothr'];
    input_expense_data['advrtpromo'] = 0.9 * input_expense_data['advrtpromo'];
    input_expense_data['officexpns'] = 0.85 * input_expense_data['officexpns'];
    input_expense_data['infotech'] = 0.85 * input_expense_data['infotech'];
    input_expense_data['interestamt'] = 0;
    input_expense_data['insurance'] = Math.min(input_expense_data['insurance'], 0.01 * input_expense_data['total_revenue']);
    input_expense_data['othremplyeebene'] = 0.85 * input_expense_data['othremplyeebene'];
    input_expense_data['pension_plan_contributions'] = Math.min(input_expense_data['pension_plan_contributions'], 2260);

    var uac_expenses = $.map(input_expense_data, function(value, index) {
        return parseInt(value);
     });

    current_expenses = current_expenses.slice(0,14);
    uac_expenses = uac_expenses.slice(0,14);

    savingsData = [current_expenses, uac_expenses];

    return savingsData;
}

function createBarGraph(savingsData) { 
    document.getElementById("svg_container").innerHTML = "";

    var n = 2, // number of layers
        m = 14; // number of samples per layer

    console.log('PRINTING OUT DATA PASSED INTO createBarGraph()');
    console.log(savingsData);

    var labels = ['Pension plan', 'Other employee benefits', 'Management',
                  'Legal', 'Accounting', 'Lobbying',
                  'Professional fundraising', 'Investment management', 'Other',
                  'Advertising and promotion', 'Office expenses',
                  'Information technology', 'Interest', 'Insurance'];

    var stack = d3.layout.stack();
    var layers = stack(d3.range(n).map(function(x) {return getData(x, savingsData); }));
    
    yGroupMax = d3.max(layers, function(layer) { return d3.max(layer, 
        function(d) { return d.y; }); });
    
    yStackMax = d3.max(layers, function(layer) { return d3.max(layer, 
        function(d) { return d.y0 + d.y; }); });

    var margin = {top: 40, right: 10, bottom: 75, left: 10};
    width = 838 - margin.left - margin.right;
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
    .tickFormat(function(d) { return convertToLabel(d, labels); })
    .orient("bottom");

    var yAxis = d3.svg.axis()
    .scale(y)
    .tickSize(3)
    .ticks(20)
    .tickPadding(0)
    .tickFormat(function(d) {return '$' + d; })
    .orient("left");

    var offset = margin.left + 40; // to move diagram right
    

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

    // .style("text-anchor","end")
    // .attr("transform", function(d) {
    //     return "rotate(-30)"
    // });

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
        return "rotate(-30)"
    });

    svg.append("g")
    .attr("class", "y axis")
    .attr("transform", "translate(0,0)")
    .call(yAxis);

    //d3.selectAll("input").on("change", change);

    change(yGroupMax, yStackMax, n);
}


function convertToLabel(d, labels) {
    if (d >= 0 && d < NUM_OF_EXPENSE_CATEGORIES) {
        var label = labels[d]
        // if (label.length > 5) {
        //     return label.substring(0,6) + '.';
        // } 
        return label;
        
    } else {
        return 'Not a valid label';
    }
} //function convertToLabel(d)

// to change graph from STACKED to GROUPED bars
function change(yGroupMax, yStackMax, numLayers) {
    if (this.value === "stacked") transitionStacked(yStackMax);
    else transitionGrouped(yGroupMax, numLayers);
}

function transitionGrouped(yGroupMax, n) {
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

function transitionStacked(yStackMax) {
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
function getData(row, data) {
    var a = data[row];
   
    var m = a.map(function(d, i) {return {x: i, y: d}; });
    console.log('getData()')
    console.log(m);
    return m;
}


// function populateForm() {
//     $('#management').val(expense_data[0][0]);
//     $('#legal').val(expense_data[0][1]);
//     $('#accounting').val(expense_data[0][2]);
//     $('#lobbying').val(expense_data[0][3]);
//     $('#professional_fundraising').val(expense_data[0][4]);
//     $('#investment_management').val(expense_data[0][5]);
//     $('#advertising').val(expense_data[0][6]);
//     $('#office_expenses').val(expense_data[0][7]);
//     $('#information_technology').val(expense_data[0][8]);
//     $('#interest_expense').val(expense_data[0][9]);
//     $('#insurance').val(expense_data[0][10]);
//     $('#employee_benefits').val(expense_data[0][11]);
//     $('#pension_plan_contributions').val(expense_data[0][12]);
//     $('#other').val(expense_data[0][13]);
// }


function createHorizontalBars(thisNonprofitRankings, numBars, gapSize, width, height) {
    var rect_container = d3.select("#svg2_container").html('');
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

    
    for (var i = 0; i < numBars; i++) {
        var strokeWidth = 2;
        if (thisNonprofitRankings[i] === 1) {
            strokeWidth = 4;
        }

        rect_container.append("line")
        .attr('x1', rectWidth - (thisNonprofitRankings[i] * rectWidth))
        .attr('y1', i*gapSize)
        .attr('x2', rectWidth - (thisNonprofitRankings[i] * rectWidth))
        .attr('y2', i*gapSize + rectHeight)
        .attr('stroke-width',2)
        .attr('stroke','white')
        .on("mouseover", function(d) {      
            div.transition()        
                .duration(200)      
                .style("opacity", .9);      
            div .html(formatTime(d.date) + "<br/>"  + d.close)  
                .style("left", (d3.event.pageX) + "px")     
                .style("top", (d3.event.pageY - 28) + "px");    
            })                  
        .on("mouseout", function(d) {       
            div.transition()        
                .duration(500)      
                .style("opacity", 0);   
        });
    }/*
    for (var j = 1; j < comparison_data.length; j++) {
        for (var i = 0; i < numBars; i++) {
            console.log('making bars: '+i+','+j);
            rect_container.append("line")
            .attr('x1', rectWidth - (parseFloat(comparison_data[j][i]) * rectWidth))
            .attr('y1', i*gapSize)
            .attr('x2', rectWidth - (parseFloat(comparison_data[j][i]) * rectWidth))
            .attr('y2', i*gapSize + rectHeight)
            .attr('stroke-width', 2)
            .attr('stroke','white')
            .on("mouseover", function(d) {      
                tooltip.transition().duration(200).style("opacity", .9);      
                tooltip.html(d)  
                  .style("left", (d3.event.pageX) + "px")     
                  .style("top", (d3.event.pageY - 28) + "px");    
            })                  
            .on("mouseout", function(d) {       
                tooltip.transition().duration(500).style("opacity", 0);   
            });
        }
    }*/
} //function createHorizontalBars

function updateTotalExpenseAndValidateFields() {

    // if the function is called on load, then no validation needed as the form
    // is pre-populated properly
    if ($(document).is(event.target)) { 
        var num = 0; // just a dummy integer so the validation passes
    } else {
        var num = $(event.target).val();
    }

    var parent = $('#' + $(event.target)[0].id).parent(); // for appending-removing error messages
    var errorMessageElement = parent.children()[parent.children.length];
    console.log(errorMessageElement);

    if (isValidInt(num)) {
        var total_expense = parseInt(
            parseInt($('#pension_plan_contributions').val()) + 
            parseInt($('#othremplyeebene').val()) + 
            parseInt($('#feesforsrvcmgmt').val()) + 
            parseInt($('#legalfees').val()) + 
            parseInt($('#accountingfees').val()) + 
            parseInt($('#feesforsrvclobby').val()) + 
            parseInt($('#profndraising').val()) + 
            parseInt($('#feesforsrvcinvstmgmt').val()) + 
            parseInt($('#advrtpromo').val()) + 
            parseInt($('#officexpns').val()) + 
            parseInt($('#infotech').val()) + 
            parseInt($('#interestamt').val()) + 
            parseInt($('#insurance').val()) + 
            parseInt($('#feesforsrvcothr').val())
        );
        var dollarized = '$' + (total_expense + '').replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,");
        $('#total_expense').html(dollarized);
        
        if (errorMessageElement) {
            $(errorMessageElement).html('');
        }

    } else {
        $(errorMessageElement).html('<br> Please enter an integer.');
    }

}

function isValidInt(text) {
    return Math.floor(text) == text && $.isNumeric(text);
}
