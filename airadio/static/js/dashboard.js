var Dashboard = function () {
  return {
    initDashboardDaterange: function () {

      var dateNow = new Date();
      var Days29Ago = new Date();
      Days29Ago.setDate(Days29Ago.getDate() - 29);
      var startDate = Days29Ago.getFullYear() + '-' + (parseInt(Days29Ago.getMonth() + 1)) + '-' + Days29Ago.getDate()
      var endDate = dateNow.getFullYear() + '-' + (parseInt(dateNow.getMonth() + 1)) + '-' + dateNow.getDate()
      changeFilter(startDate, endDate);
      $('#dashboard-report-range').daterangepicker({
          opens: ('left'),
          startDate: moment().subtract('days', 29),
          endDate: moment(),
          minDate: '01/01/2012',
          maxDate: '12/31/2014',
          dateLimit: {
            days: 60
          },
          showDropdowns: false,
          showWeekNumbers: true,
          timePicker: false,
          timePickerIncrement: 1,
          timePicker12Hour: true,
          ranges: {
            'Today': [moment(), moment()],
            'Yesterday': [moment().subtract('days', 1), moment().subtract('days', 1)],
            'Last 7 Days': [moment().subtract('days', 6), moment()],
            'Last 30 Days': [moment().subtract('days', 29), moment()],
            'This Month': [moment().startOf('month'), moment().endOf('month')],
            'Last Month': [moment().subtract('month', 1).startOf('month'), moment().subtract('month', 1).endOf('month')]
          },
          buttonClasses: ['btn'],
          applyClass: 'blue',
          cancelClass: 'default',
          format: 'MM/DD/YYYY',
          separator: ' to ',
          locale: {
            applyLabel: 'Apply',
            fromLabel: 'From',
            toLabel: 'To',
            customRangeLabel: 'Custom Range',
            daysOfWeek: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
            monthNames: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
            firstDay: 1
          }
        },
        function (start, end) {
          changeFilter(start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD'))
          $('#dashboard-report-range span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
        }
      );

      $('#dashboard-report-range span').html(moment().subtract('days', 29).format('MMMM D, YYYY') + ' - ' + moment().format('MMMM D, YYYY'));
      $('#dashboard-report-range').show();
    }
  };
}();

function changeFilter(start, end) {
  $.ajax({
    url: ".",
    type: 'GET',
    data: {
      'start': start,
      'end': end
    },
    success: function (data) {
      if (data.status == true) {
        $('#stats_top_bar').html(data.stats);
        $('#topsongs').html(data.top_songs);
        // music_research($.parseJSON(data.music_research));

      } else {
        alert('No records found.')
      }
    }
  });
}

function music_research(music_data) {
  let music_research_stats = $('#music-research-stats');
  if (music_research_stats && music_research_stats.size() != 0) {

    music_research_stats.hide();
    music_research_stats.show();

    var sin = [],
      cos = [];
    for (var i = 0; i < 14; i += 0.5) {
      sin.push([i, Math.sin(i)]);
      cos.push([i, Math.cos(i)]);
    }

    // $.plot(music_research_stats,
    //   music_data, {
    //     series: {
    //       lines: {
    //         show: true
    //       },
    //       points: {
    //         show: true
    //       }
    //     },
    //     grid: {
    //       hoverable: true
    //     },
    //     yaxis: {
    //       min: 0,
    //       max: 100
    //     }
    //   });

    $("#flot-demo").bind("plothover", function (event, pos, item) {
      if ($("#enablePosition:checked").length > 0) {
        var str = "(" + pos.x.toFixed(2) + ", " + pos.y.toFixed(2) + ")";
        $("#hoverdata").text(str);
      }
    });
  }
}
