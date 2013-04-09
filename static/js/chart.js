$(document).ready(function() {
  $('#chart-note-link').on('click', function(e) {
    e.preventDefault();
    $("#chart-note").slideToggle('slow');
  });
});
