var Analytics = function () {
  return {
    initAnalyticsDaterange: function () {

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

function InitAllPieCharts(analytics) {
  var age = {
    male: analytics.male,
    female: analytics.female
  }
  var platform = {
    iphone: analytics.iphone,
    android: analytics.android,
    web_palyer: analytics.web_palyer
  }
  InitAgeProfile(age);
  InitPlatformUsage(platform);
}

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
        InitAllPieCharts(data.analytics);
        $('#stats_top_bar').html(data.stats);
        $('#anl_tsu_tbl').html(data.html);
      } else {
        alert('No records found.')
      }
    }
  });
}

function InitPlatformUsage(platform) {
  var platformUsageData = [{
      label: "iPhone - " + platform.iphone + "%",
      data: platform.iphone,
      color: "#308eef"
    },
    {
      label: "Android - " + platform.android + "%",
      data: platform.android,
      color: "#71a100"
    },
    {
      label: "WebPlayer - " + platform.web_palyer + "%",
      data: platform.web_palyer,
      color: "#d1ca00"
    }
  ]

  // $.plot($("#platform-usage-stats"), platformUsageData, {
  //   series: {
  //     pie: {
  //       show: true
  //     }
  //   },
  //   grid: {
  //     hoverable: true,
  //     clickable: true
  //   },
  //   redraw: true
  // });
}

function InitAgeProfile(age) {
  var ageProfileData = [{
      label: "Male - " + age.male + "%",
      data: age.male,
      color: "#4DA74D"
    },
    {
      label: "Female - " + age.female + "%",
      data: age.female,
      color: "#DF3131"
    },
  ]

  // $.plot($("#age-profile-stats"), ageProfileData, {
  //   series: {
  //     pie: {
  //       show: true
  //     }
  //   },
  //   grid: {
  //     hoverable: true,
  //     clickable: true
  //   },
  //   redraw: true
  // });
}
