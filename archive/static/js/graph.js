var yearCountChart = dc.barChart('#review-count-chart');


$('document').ready(function() {
    $('#btn').click(function(e) {
        e.preventDefault();
        var user = $('#input').val();
        $('#btn').hide();


        d3.json('/data?user=' + user)
        .then(function (mvlist) {
            $('#btn').show();
            console.log(mvlist);
            // my code
            var totalWidth = 990;
            var height = 300;

            var maxYear = new Date().getFullYear();
            var minYear = maxYear;

            mvlist.forEach(function (d) {
                d.dv = new Date(d.date_view);
                d.dvYear = d.dv.getFullYear();
                d.rmy = +d.rating_my;

                if(d.dvYear < minYear) {
                    minYear = d.dvYear;
                }
            });

            console.log(mvlist);

            movies = crossfilter(mvlist);
            var all = movies.groupAll();

            var yearlyDimension = movies.dimension(function (d) {
                return d.dvYear;
            });
            var ratingMyDimension = movies.dimension(function (d)) {
                return d.rating_my;
            }

            var yearGroup = yearlyDimension.group().reduceCount();
            var ratingMyGroup = yearlyDimension.group().reduceCount();

            yearCountChart
                .dimension(yearlyDimension)
                .group(yearGroup)
                .width(totalWidth / 2.1)
                .height(200)
                .x(d3.scaleLinear().domain([minYear, maxYear+1]))
                .renderHorizontalGridLines(true)
                .filterPrinter(function (filters) {
                    var filter = filters[0], s = '';
                    s += numberFormat(filter[0]) + ' -> ' + numberFormat(filter[1]);
                    return s;
                })
                .xAxis().tickFormat(d3.format("d"));

            yearCountChart.xAxis().tickFormat(
                function (v) {
                    return v;
                });
            yearCountChart.yAxis().ticks(10);

            dc.renderAll();


        })
        .catch(function(e) {
            console.error(e);
            $('#btn').show();
        });

//        $.ajax({
//            url: '/data?user=' + user
//        }).done(function(data) {
//            console.log(data);
//        }).always(function() {
//            $('#btn').show();
//        });
    });
});
//d3.json("/data?user=4476933").then(function (data) {
//    console.log(data);
//})