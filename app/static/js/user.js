var yearCountChart = dc.barChart('#review-count-chart');
var monthCountChart = dc.barChart('#review-month-count-chart')
var myRatingBarChart = dc.barChart('#my-rating-chart-bar');
var myRatingRowChart = dc.rowChart('#my-rating-chart-row');
var myRatingPieChart = dc.pieChart("#my-rating-pie-chart");
var movieCount = dc.dataCount('.dc-data-count');
var movieTable = dc.dataTable('.dc-data-table');

//var mvlist = {{mvlist|safe}};

console.log(mvlist);

// my code
var numberFormat = d3.format('d')
var totalWidth = 990;
var height = 300;

var maxYear = new Date().getFullYear();
var minYear = maxYear;
var minMonth = d3.timeMonth(new Date());
var maxMonth = minMonth;

mvlist.forEach(function(d) {
    d.mv_url = d.movieurl;
    d.name = d.moviename;
    d.mv_url = d.movieurl;
    d.date_view = d.dateviewed;
    d.dv = new Date(d.date_view);
    d.dvYear = d.dv.getFullYear();
    d.dvMonth = d3.timeMonth(d.dv); // return the Standard Time the first day of every month
    d.rmy = +d.rating_my;

    if (d.dvYear < minYear) {
        minYear = d.dvYear;
    };

    if (d.dvMonth < minMonth) {
        minMonth = d.dvMonth;
    }
});

// console.log(mvlist);

movies = crossfilter(mvlist);
var all = movies.groupAll();

var dateDimension = movies.dimension(function(d) {
    return d.dv;
});
var yearlyDimension = movies.dimension(function(d) {
    return d.dvYear;
});
var ratingMyDimension = movies.dimension(function(d) {
    return d.rating_my;
});
var monthlyDimension = movies.dimension(function(d) {
    return d.dvMonth;
});

var yearGroup = yearlyDimension.group().reduceCount();
var ratingMyGroup = ratingMyDimension.group().reduceCount();
var monthGroup = monthlyDimension.group().reduceCount();

// console.log(ratingMyGroup);
// console.log(dateDimension.top(Infinity));
console.log('monthGroup', monthGroup.top(Infinity));

yearCountChart
    .dimension(yearlyDimension)
    .group(yearGroup)
    .width(totalWidth / 2.1)
    .height(200)
    .round(dc.round.floor)
    .alwaysUseRounding(true)
    .x(d3.scaleLinear().domain([minYear, maxYear + 1]))
    .renderHorizontalGridLines(true)
    .filterPrinter(function(filters) {
        var filter = filters[0],
            s = '';
        s += '[' + Math.ceil(filter[0]) + ' -> ' + Math.floor(filter[1]) + ']';
        return s;
    })
    .xAxis().tickFormat(d3.format("d"));

yearCountChart.yAxis().ticks(10);

myRatingPieChart
    .width(totalWidth / 2.1)
    .height(200)
    .radius(80)
    // .innerRadius(30)
    .dimension(ratingMyDimension)
    .group(ratingMyGroup)
    // .ordinalColors(d3.schemeCategory10)
    .label(function(d) {
        if (myRatingPieChart.hasFilter() && !myRatingPieChart.hasFilter(d.key)) {
            return d3.format('d')(d.key) + 'star' + '(0%)';
        }
        var label = d3.format('d')(d.key) + 'star';
        if (all.value()) {
            label += '(' + Math.floor(d.value / all.value() * 100) + '%)';
        }
        return label;
    });

monthCountChart
    .dimension(monthlyDimension)
    .group(monthGroup)
    .width(totalWidth)
    .height(200)
    .gap(0.3)
    .x(d3.scaleTime().domain([minMonth, maxMonth]))
    .round(dc.round.floor)
    .alwaysUseRounding(true)
    .renderHorizontalGridLines(true)
    .filterPrinter(function(filters) {
        var filter = filters[0],
            s = '';
        // console.log('filter', filter);
        s += '[' + d3.timeFormat("%b-%y")(filter[0]) + ' -> ' + d3.timeFormat("%b-%y")(filter[1]) + ']';
        return s; // todo-bug: filter[0] need to be the next month
    })
    .xAxis().tickFormat(d3.timeFormat("%b-%y"));

monthCountChart.xAxis().ticks(monthGroup.length);

console.log('minMonth', minMonth);
console.log('maxMonth', maxMonth);
console.log('total months', monthGroup.all().length);
console.log(monthCountChart);


myRatingBarChart
    .dimension(ratingMyDimension)
    .group(ratingMyGroup)
    .width(totalWidth / 2.1)
    .height(200)
    .brushOn(false)
    .elasticY(true)
    .centerBar(true)
    .x(d3.scaleLinear().domain([-1, 6]))
    .renderHorizontalGridLines(true)
    .xAxis().tickFormat(d3.format("d"));

myRatingBarChart.xAxis().ticks(8);
myRatingBarChart.yAxis().ticks(10);

myRatingRowChart
    .width(totalWidth / 2.1)
    .height(200)
    .group(ratingMyGroup)
    .dimension(ratingMyDimension)
    .ordinalColors(d3.schemeCategory10)
    .ordering(function(d) {
        return -d.key;
    })
    .label(function(d) {
        if (d.key > 0) {
            return d3.format('d')(d.key) + ' star';
        } else {
            return 'no rating';
        }
    })
    .title(function(d) {
        return d.value;
    })
    .elasticX(true)
    .xAxis().ticks(10);

movieCount
    .dimension(movies)
    .group(all)
    .html({
        some: '<strong>%filter-count</strong> selected out of <strong>%total-count</strong> records' +
            ' | <a href=\'javascript:dc.filterAll(); dc.renderAll();\'>Reset All</a>',
        all: 'All records selected. Please click on the graph to apply filters.'
    });

movieTable /* dc.dataTable('.dc-data-table', 'chartGroup') */
    .dimension(dateDimension)
    .group(function(d) {
        return "";
    })
    .size(100)
    .columns([{
            label: 'Date Viewed',
            format: function(d) {
                return d.date_view;
            }
        },
        {
            label: 'Title',
            format: function(d) {
                return "<a href=" + d.mv_url + ">" + d.name + "</a>";
            }
        },
        {
            label: 'My Rating',
            format: function(d) {
                return '&starf;'.repeat(d.rmy);
            }
        }
    ])
    .sortBy(function(d) {
        return d.dv;
    })
    .order(d3.descending)
    .on('renderlet', function(table) {
        table.selectAll('.dc-table-group').classed('info', true);
    });

dc.renderAll();