$(document).ready(function() {
  spinning_gif = '<img src="/static/img/89.gif" />';
  if (!window.console) window.console = {};
  if (!window.console.log) window.console.log = function() {};
  app = $.sammy(function() { with(this) {
    get('#/test', function() { with(this) {
      $('#test').append('link works<br />');
    }});
    get('#/fb-stream', function() { with(this) {
      $('#fb-stream').html(spinning_gif);
      $.get('/a/fb-stream', function (data) {
        $('#fb-stream').html(data);
      });
    }});
  }});

  $(function() {
    app.run();
  });
});
