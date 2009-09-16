$(document).ready(function() {
  if (!window.console) window.console = {};
  if (!window.console.log) window.console.log = function() {};
  app = $.sammy(function() { with(this) {
    get('#/test', function() { with(this) {
      $('#test').append('link works<br />');
    }});
  }});

  $(function() {
    app.run();
  });
});
