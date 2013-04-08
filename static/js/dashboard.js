$(document).ready(function() {
  $('.tab').on('click', function() {
    var timeVal;
    if (!($(this).hasClass === 'selected')) {
      timeVal = $(this).attr('id');
      $(this).addClass('selected')
            .siblings().removeClass('selected')
            .find('#date-input').attr('value', timeVal);

      Niko.changeGreeting(timeVal);
    }
  });
});

Niko = {
  changeGreeting: function(timeVal) {
    if (timeVal === 'today') {
      $('#greeting').html("How's it going");
    }
    else if (timeVal === 'yesterday') {
      $('#greeting').html("How was yesterday");
    }
  }
};
