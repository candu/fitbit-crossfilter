d3.json("/get-user-data", function(json) {
  // TODO: build time series in Python instead, store those in DB
  var timeSeries = json.map(function(dailyData) {
    // time
    var date = dailyData["activeScore"]["activities-activeScore"][0]["dateTime"];
    var timestamp = +new Date(date + " 00:00:00");
    // daily activity metrics
    var activeScore = +dailyData["activeScore"]["activities-activeScore"][0]["value"];
    var minutesSedentary = +dailyData["minutesSedentary"]["activities-minutesSedentary"][0]["value"];
    var minutesLightlyActive = +dailyData["minutesLightlyActive"]["activities-minutesLightlyActive"][0]["value"];
    var minutesFairlyActive = +dailyData["minutesFairlyActive"]["activities-minutesFairlyActive"][0]["value"];
    var minutesVeryActive = +dailyData["minutesVeryActive"]["activities-minutesVeryActive"][0]["value"];
    // daily sleep metrics
    var awakeningsCount = +dailyData["awakeningsCount"]["sleep-awakeningsCount"][0]["value"];
    var efficiency = +dailyData["efficiency"]["sleep-efficiency"][0]["value"];
    var minutesToFallAsleep = +dailyData["minutesToFallAsleep"]["sleep-minutesToFallAsleep"][0]["value"];
    var startTime = +dailyData["startTime"]["sleep-startTime"][0]["value"];
    var timeInBed = +dailyData["timeInBed"]["sleep-timeInBed"][0]["value"];
    // daily direct data 
    var totalCalories = +dailyData["calories"]["activities-log-calories"][0]["value"];
    var totalFloors = +dailyData["floors"]["activities-log-floors"][0]["value"];
    var totalSteps = +dailyData["steps"]["activities-log-steps"][0]["value"];
    var dailyTimeSeries = [];
    for (var i = 0; i < 1440; i++) {
      dailyTimeSeries.push({
        // time
        timestamp: timestamp,
        // daily series
        activeScore: activeScore,
        minutesSedentary: minutesSedentary,
        minutesLightlyActive: minutesLightlyActive,
        minutesFairlyActive: minutesFairlyActive,
        minutesVeryActive: minutesVeryActive,
        awakeningsCount: awakeningsCount,
        efficiency: efficiency,
        minutesToFallAsleep: minutesToFallAsleep,
        startTime: startTime,
        timeInBed: timeInBed,
        totalCalories: totalCalories,
        totalFloors: totalFloors,
        totalSteps: totalSteps,
        // intraday series
        calories: +dailyData["calories"]["activities-log-calories-intraday"]["dataset"][i]["value"],
        floors: +dailyData["floors"]["activities-log-floors-intraday"]["dataset"][i]["value"],
        steps: +dailyData["steps"]["activities-log-steps-intraday"]["dataset"][i]["value"],
      });
      timestamp += 60 * 1000;
    }
    return dailyTimeSeries;
  });
  timeSeries = [].concat.apply([], timeSeries);

  // crossfilter dimensions and groups
  var fitbit = crossfilter(timeSeries);
  var allGrp = fitbit.groupAll();
  var dateDim = fitbit.dimension(function(d) {
    return d3.time.day(new Date(d.timestamp));
  });
  var dateGrp = dateDim.group();
  var hourDim = fitbit.dimension(function(d) {
    var dDate = new Date(d.timestamp);
    return dDate.getHours() + dDate.getMinutes() / 60;
  });
  var hourGrp = hourDim.group(Math.floor);

  var today = new Date();
  var endDate = new Date(
      today.getFullYear(),
      today.getMonth(),
      today.getDate(),
      0, 0, 0);
  var startDate = new Date(+endDate - 90 * 24 * 60 * 60 * 1000);
  console.log(endDate);
  console.log(startDate);

  var charts = [
    barChart()
        .dimension(dateDim)
        .group(dateGrp)
      .x(d3.time.scale()
        .domain([startDate, endDate])
        .rangeRound([0, 10 * 90])),
    barChart()
        .dimension(hourDim)
        .group(hourGrp)
      .x(d3.scale.linear()
        .domain([0, 24])
        .rangeRound([0, 10 * 24]))
  ];

  var chart = d3.selectAll(".chart")
    .data(charts)
    .each(function(chart) {
      chart.on("brush", renderAll).on("brushend", renderAll);
    });

  renderAll();

  function render(method) {
    d3.select(this).call(method);
  }

  // Whenever the brush moves, re-rendering everything.
  function renderAll() {
    chart.each(render);
  }

  window.filter = function(filters) {
    filters.forEach(function(d, i) { charts[i].filter(d); });
    renderAll();
  };

  window.reset = function(i) {
    charts[i].filter(null);
    renderAll();
  };

  // from crossfilter demo at http://square.github.com/crossfilter/
  function barChart() {
    if (!barChart.id) barChart.id = 0;

    var margin = {top: 10, right: 10, bottom: 20, left: 10},
        x,
        y = d3.scale.linear().range([100, 0]),
        id = barChart.id++,
        axis = d3.svg.axis().orient("bottom"),
        brush = d3.svg.brush(),
        brushDirty,
        dimension,
        group,
        round;

    function chart(div) {
      var width = x.range()[1],
          height = y.range()[0];

      y.domain([0, group.top(1)[0].value]);

      div.each(function() {
        var div = d3.select(this),
            g = div.select("g");

        // Create the skeletal chart.
        if (g.empty()) {
          div.select(".title").append("a")
              .attr("href", "javascript:reset(" + id + ")")
              .attr("class", "reset")
              .text("reset")
              .style("display", "none");

          g = div.append("svg")
              .attr("width", width + margin.left + margin.right)
              .attr("height", height + margin.top + margin.bottom)
            .append("g")
              .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

          g.append("clipPath")
              .attr("id", "clip-" + id)
            .append("rect")
              .attr("width", width)
              .attr("height", height);

          g.selectAll(".bar")
              .data(["background", "foreground"])
            .enter().append("path")
              .attr("class", function(d) { return d + " bar"; })
              .datum(group.all());

          g.selectAll(".foreground.bar")
              .attr("clip-path", "url(#clip-" + id + ")");

          g.append("g")
              .attr("class", "axis")
              .attr("transform", "translate(0," + height + ")")
              .call(axis);

          // Initialize the brush component with pretty resize handles.
          var gBrush = g.append("g").attr("class", "brush").call(brush);
          gBrush.selectAll("rect").attr("height", height);
          gBrush.selectAll(".resize").append("path").attr("d", resizePath);
        }

        // Only redraw the brush if set externally.
        if (brushDirty) {
          brushDirty = false;
          g.selectAll(".brush").call(brush);
          div.select(".title a").style("display", brush.empty() ? "none" : null);
          if (brush.empty()) {
            g.selectAll("#clip-" + id + " rect")
                .attr("x", 0)
                .attr("width", width);
          } else {
            var extent = brush.extent();
            g.selectAll("#clip-" + id + " rect")
                .attr("x", x(extent[0]))
                .attr("width", x(extent[1]) - x(extent[0]));
          }
        }

        g.selectAll(".bar").attr("d", barPath);
      });

      function barPath(groups) {
        var path = [],
            i = -1,
            n = groups.length,
            d;
        while (++i < n) {
          d = groups[i];
          path.push("M", x(d.key), ",", height, "V", y(d.value), "h9V", height);
        }
        return path.join("");
      }

      function resizePath(d) {
        var e = +(d == "e"),
            x = e ? 1 : -1,
            y = height / 3;
        return "M" + (.5 * x) + "," + y
            + "A6,6 0 0 " + e + " " + (6.5 * x) + "," + (y + 6)
            + "V" + (2 * y - 6)
            + "A6,6 0 0 " + e + " " + (.5 * x) + "," + (2 * y)
            + "Z"
            + "M" + (2.5 * x) + "," + (y + 8)
            + "V" + (2 * y - 8)
            + "M" + (4.5 * x) + "," + (y + 8)
            + "V" + (2 * y - 8);
      }
    }

    brush.on("brushstart.chart", function() {
      var div = d3.select(this.parentNode.parentNode.parentNode);
      div.select(".title a").style("display", null);
    });

    brush.on("brush.chart", function() {
      var g = d3.select(this.parentNode),
          extent = brush.extent();
      if (round) g.select(".brush")
          .call(brush.extent(extent = extent.map(round)))
        .selectAll(".resize")
          .style("display", null);
      g.select("#clip-" + id + " rect")
          .attr("x", x(extent[0]))
          .attr("width", x(extent[1]) - x(extent[0]));
      dimension.filterRange(extent);
    });

    brush.on("brushend.chart", function() {
      if (brush.empty()) {
        var div = d3.select(this.parentNode.parentNode.parentNode);
        div.select(".title a").style("display", "none");
        div.select("#clip-" + id + " rect").attr("x", null).attr("width", "100%");
        dimension.filterAll();
      }
    });

    chart.margin = function(_) {
      if (!arguments.length) return margin;
      margin = _;
      return chart;
    };

    chart.x = function(_) {
      if (!arguments.length) return x;
      x = _;
      axis.scale(x);
      brush.x(x);
      return chart;
    };

    chart.y = function(_) {
      if (!arguments.length) return y;
      y = _;
      return chart;
    };

    chart.dimension = function(_) {
      if (!arguments.length) return dimension;
      dimension = _;
      return chart;
    };

    chart.filter = function(_) {
      if (_) {
        brush.extent(_);
        dimension.filterRange(_);
      } else {
        brush.clear();
        dimension.filterAll();
      }
      brushDirty = true;
      return chart;
    };

    chart.group = function(_) {
      if (!arguments.length) return group;
      group = _;
      return chart;
    };

    chart.round = function(_) {
      if (!arguments.length) return round;
      round = _;
      return chart;
    };

    return d3.rebind(chart, brush, "on");
  }
});
