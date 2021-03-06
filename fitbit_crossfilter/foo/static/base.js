var loadStart = +new Date();
d3.json("/get-user-data", function(json) {
  var timeSeries = json.map(function(dailyData) {
    return dailyData.ts.map(function(data) {
      var elem = {
        activeScore: dailyData.summary.activeScore,
        awakeningsCount: dailyData.summary.awakeningsCount,
        minutesToFallAsleep: dailyData.summary.minutesToFallAsleep,
        timeInBed: dailyData.summary.timeInBed,
      };
      for (var i = 0; i < data.length; i++) {
        elem[dailyData.ts_columns[i]] = data[i];
      }
      return elem;
    });
  });
  timeSeries = [].concat.apply([], timeSeries);

  var startTime = new Date(timeSeries[0].timestamp);
  var endTime = new Date(timeSeries[timeSeries.length - 1].timestamp);
  var startDate = new Date(
    startTime.getFullYear(),
    startTime.getMonth(),
    startTime.getDate(),
    0, 0, 0);
  var endDate = new Date(
    endTime.getFullYear(),
    endTime.getMonth(),
    endTime.getDate(),
    0, 0, 0);

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
  var stepsDim = fitbit.dimension(function(d) {
    return Math.min(200, d.steps);
  });
  var stepsGrp = stepsDim.group(function(d) {
    return Math.floor(d / 5) * 5;
  });
  var caloriesDim = fitbit.dimension(function(d) {
    return Math.min(25, d.calories);
  });
  var caloriesGrp = caloriesDim.group(function(d) {
    return Math.floor(d);
  });
  var floorsDim = fitbit.dimension(function(d) {
    return Math.min(10, d.floors);
  });
  var floorsGrp = floorsDim.group(function(d) {
    return d;
  });
  var activeScoreDim = fitbit.dimension(function(d) {
    return Math.min(2500, d.activeScore) / 1000;
  });
  var activeScoreGrp = activeScoreDim.group(function(d) {
    return Math.floor(d / 0.1) * 0.1;
  });
  var awakeningsCountDim = fitbit.dimension(function(d) {
    return Math.min(15, d.awakeningsCount);
  });
  var awakeningsCountGrp = awakeningsCountDim.group(function(d) {
    return d;
  });
  var minutesToFallAsleepDim = fitbit.dimension(function(d) {
    return Math.min(60, d.minutesToFallAsleep);
  });
  var minutesToFallAsleepGrp = minutesToFallAsleepDim.group(function(d) {
    return Math.floor(d / 3) * 3;
  });
  var timeInBedDim = fitbit.dimension(function(d) {
    return d.timeInBed / 60;
  });
  var timeInBedGrp = timeInBedDim.group(function(d) {
    return Math.floor(d);
  });

  var charts = [
    barChart()
        .dimension(dateDim)
        .group(dateGrp)
      .x(d3.time.scale()
        .domain([startDate, endDate])
        .rangeRound([0, 10 * 60])),
    barChart()
        .dimension(hourDim)
        .group(hourGrp)
      .x(d3.scale.linear()
        .domain([0, 24])
        .rangeRound([0, 10 * 24])),
    barChart()
        .dimension(stepsDim)
        .group(stepsGrp)
      .x(d3.scale.linear()
        .domain([0, 200])
        .rangeRound([0, 10 * 41])),
    barChart()
        .dimension(caloriesDim)
        .group(caloriesGrp)
      .x(d3.scale.linear()
        .domain([0, 25])
        .rangeRound([0, 10 * 26])),
    barChart()
        .dimension(floorsDim)
        .group(floorsGrp)
      .x(d3.scale.linear()
        .domain([0, 10])
        .rangeRound([0, 10 * 11])),
    barChart()
        .dimension(activeScoreDim)
        .group(activeScoreGrp)
      .x(d3.scale.linear()
        .domain([0, 2.5])
        .rangeRound([0, 10 * 26])),
    barChart()
        .dimension(awakeningsCountDim)
        .group(awakeningsCountGrp)
      .x(d3.scale.linear()
        .domain([0, 15])
        .rangeRound([0, 10 * 16])),
    barChart()
        .dimension(minutesToFallAsleepDim)
        .group(minutesToFallAsleepGrp)
      .x(d3.scale.linear()
        .domain([0, 60])
        .rangeRound([0, 10 * 21])),
    barChart()
        .dimension(timeInBedDim)
        .group(timeInBedGrp)
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
  var loadTime = +new Date() - loadStart;
  d3.select("#footer").text("Page loaded in " + loadTime + " ms");

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

  window.resetAll = function() {
    for (var i = 0; i < charts.length; i++) {
        charts[i].filter(null);
    }
    renderAll();
  }

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
