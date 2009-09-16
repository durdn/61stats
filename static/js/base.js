$(document).ready(function() {
  if (!window.console) window.console = {};
  if (!window.console.log) window.console.log = function() {};
  app = $.sammy(function() { with(this) {
    get('#/test', function() { with(this) {
      $('#test').append('link works<br />');
    }});
    get('#/fb-stream', function() { with(this) {
      $('#fb-stream').html('<img src="/static/img/arrows64.gif" />');
      $.get('/a/fb-stream', function (data) {
        $('#fb-stream').html(data);
      });
    }});
  }});

  $(function() {
    app.run();
  });
});
