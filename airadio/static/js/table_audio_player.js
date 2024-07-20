$(document).ready(function () {
  audio_player = null;
  current_audio_id = null;
});

function playAudio(id) {
  if (audio_player == null && current_audio_id == null) {
    createAudio(id);
    startAudio(id);
  } else if (audio_player != null && current_audio_id == id) {
    if (audio_player.paused) {
      startAudio(id);
    } else {
      pauseAudio(id);
    }
  } else if (audio_player != null && current_audio_id != id) {
    pauseAudio(current_audio_id);
    destroyAudio();
    createAudio(id);
    startAudio(id);
  } else {
    alert("Error");
  }
}

function createAudio(id) {
  audio_player = new Audio();
  audio_player.src = $('#id_audio' + id).attr("data-url");
  audio_player.onended = function () {
    pauseAudio(id);
    destroyAudio();
  };
}

function startAudio(id) {
  audio_player.play();
  current_audio_id = id;
  const toggle_play_button = document.querySelector('#id_audio' + id);
  toggle_play_button.children[0].src = toggle_play_button.children[0].src.replace('play', 'pause');
}

function pauseAudio(id) {
  audio_player.pause();
  const toggle_play_button = document.querySelector('#id_audio' + id);
  toggle_play_button.children[0].src = toggle_play_button.children[0].src.replace('pause', 'play');
}

function destroyAudio() {
  audio_player.currentTime = 0;
  audio_player.remove();
  audio_player = null;
}
