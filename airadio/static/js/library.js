$(document).ready(function () {
  $('#id_check_all_library').click(function () {
    var $this = $(this);
    if ($this.is(':checked')) {
      $("#LibraryFormID input[type=checkbox]").each(function () {
        $(this).prop("checked", true);
      });
    } else {
      $("#LibraryFormID input[type=checkbox]").each(function () {
        $(this).prop("checked", false);
      });
    }
  });

  $('#id_check_all_stations').click(function () {
    var $this = $(this);
    if ($this.is(':checked')) {
      $("#IDstationForm input[type=checkbox]").each(function () {
        $(this).prop("checked", true);
      });
    } else {
      $("#IDstationForm input[type=checkbox]").each(function () {
        $(this).prop("checked", false);
      });
    }
  });
});

function changeRatingStars(val, element) {
  var stars = 0;
  if (val > 0 && val < 26) {
    stars = 1;
  }
  if (val > 25 && val < 51) {
    stars = 2;
  }
  if (val > 50 && val < 76) {
    stars = 3;
  }
  if (val > 75 && val < 101) {
    stars = 4;
  }
  if (val > 100) {
    stars = 5;
  }
  if (val < 1 || val == '') {
    stars = 0;
  }
  $(element).find(".fa-star").each(function (index) {
    if (index < stars) {
      $(this).addClass("text-amber-500");
      $(this).removeClass("text-white");
    } else {
      $(this).addClass("text-white");
      $(this).removeClass("text-amber-500");
    }
  });
}

function EditStationPoints() {
  var len = $("#IDstationForm input[name='library']:checked").length;
  if (len > 1) {
    alert('You must select only a single song for editing.');
  }
  if (len == 0) {
    alert('Please select a song.');
  }

  if (len == 1) {
    var element = "#IDstationForm input[name='library']:checked";
    $('#station_entry').val($(element).val());
    var title = $(element).closest('td').next('td').text();
    $('#edit_station_points').find('h4').text(title);
    var src = $(element).closest('td').next('td').next('td').next('td').find('img').attr('src');
    $('#stationpointStars').find('img').attr('src', src);
    var points = $(element).closest('td').next('td').next('td').next('td').find('img').attr('alt');
    $('#station_point').val(points);
    $('#edit_station_points').modal();
  }
}

function UpdateStationPoints() {
  var value = $('#station_point').val();
  if (value == '') {
    $('#station_point').closest('.form-group').addClass('has-error');
  }

  $.ajax({
    data: $("#IDstationPoints").serialize(),
    type: 'post',
    url: $("#IDstationPoints").attr('action'),
    success: function (data) {
      if (data.status == true) {
        $('#close_edit_station_points').click();
        $('#refresh_btn').click();
      }
    },
    error: function (e) {
      alert('error');
    }
  });
}
