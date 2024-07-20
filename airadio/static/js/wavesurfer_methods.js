'use strict';

let wavesurfer = null;
let wsRegions = null;

function createWaveform() {
  $('#wavesurfer_loading').show();
  wavesurfer = WaveSurfer.create({
    container: '#waveform',
    waveColor: '#9ca3af',
    progressColor: '#ff5500',
    height: 120,
    url: $('#waveform').attr("data-url"),
    xhr: {
      cache: "default",
      mode: "cors",
      method: "GET",
      credentials: "include",
      headers: [
        { key: "cache-control", value: "no-cache" },
        { key: "pragma", value: "no-cache" }
      ]
    }
  });

  wavesurfer.once('ready', () => {
    $('#wavesurfer_loading').hide();
    wsRegions = wavesurfer.registerPlugin(WaveSurfer.Regions.create());
    createWaveformButton();
    loadInitialMarkers();
    wsRegions.on('region-updated', (region) => {
      $('#' + region.id).val(formatSecondsToMilliseconds(region.start));
    });
    $('#id_duration').val(formatSecondsToMilliseconds(wavesurfer.getDuration()));

    const slider = document.getElementById('waveform-zoom');
    slider.addEventListener('input', (e) => {
      const minPxPerSec = e.target.valueAsNumber;
      wavesurfer.zoom(minPxPerSec);
    })
  });
}

function createWaveformButton() {
  $('.disabled_waveform_button').attr("disabled", false);
  const waveform_toggle_button = document.querySelector('#waveform_toggle_button');
  waveform_toggle_button.disabled = false;
  waveform_toggle_button.addEventListener("click", function (e) {
    e.preventDefault();
    e.stopPropagation();
    wavesurfer.playPause();
    waveform_toggle_button.children[0].src = wavesurfer.isPlaying() ? '/static/images/pause_button_white.svg' : '/static/images/play_button_white.svg';
  });
}

function setMarkerFromInput(markerId, label) {
  var input_value = $('#' + markerId).val();
  if (input_value) {
    addWSRegion(markerId, formatMillisecondsToSeconds(input_value), label);
  }
}

function setMarker(markerId, label) {
  var current_time = wavesurfer.getCurrentTime();
  $('#' + markerId).val(formatSecondsToMilliseconds(current_time));

  let existing_marker = wsRegions.getRegions().find((element) => element.id == markerId);
  if (existing_marker) {
    existing_marker.setOptions({
      start: current_time,
      end: current_time
    });
  } else {
    addWSRegion(markerId, current_time, label);
  }
}

function addWSRegion(markerId, time, label) {
  const content = document.createElement('div');
  content.style.height = "100%";
  content.innerHTML = '<div style="height:100%;display:flex;align-items:center;padding-left:2px;"><p style="margin:0;font-size:12px;white-space:nowrap;background-color:white;border-radius:50%;height:32px;width:32px;line-height:32px;flex-shrink:0;text-align:center;">' + label + '</p></div>';
  wsRegions.addRegion({
    id: markerId,
    start: time,
    content: content,
    color: '#000000',
    drag: true
  });
}

function startAtMarker(markerId) {
  if (wavesurfer && $('#' + markerId).val()) {
    wavesurfer.setTime(formatMillisecondsToSeconds($('#' + markerId).val()));
    wavesurfer.play();
    const waveform_toggle_button = document.querySelector('#waveform_toggle_button');
    waveform_toggle_button.children[0].src = '/static/images/pause_button_white.svg';
  }
}

function formatSecondsToMilliseconds(seconds) {
  return Math.round(seconds * 1000);
}

function formatMillisecondsToSeconds(milliseconds) {
  return milliseconds / 1000;
}
