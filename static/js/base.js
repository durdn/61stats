$(document).ready(function() {
  spinning_gif = '<img src="/static/img/89.gif" />';
  if (!window.console) window.console = {};
  if (!window.console.log) window.console.log = function() {};
  //data table connect
  $('#bumps-table').dataTable();

  //sammy routes definitions
  app = $.sammy(function() { with(this) {
    get('#/user/:username/:reload', function() { with(this) {
      $.get('/collect/' + params['username'] + '/1', function (data) {
        $("#progress-bar").progressBar(0);
    	var response = eval('(' + data + ')');
    	if (response['result'] == 'OK') {
            $('#reputation-bumps').html(response['numpages']).fadeIn();
            $('#reputation-bumps').append(response['page']).fadeIn();
    	}
      });
    }});
    get('#/user/:username', function() { with(this) {
      //$('#reputation-bumps').html(spinning_gif);
      $.get('/user/' + params['username'], function (data) {
        $('#reputation-bumps').html(data).fadeIn();
        $('#bumps-table').dataTable({
          "bSort": true,
          "bStateSave": true,
          "sPaginationType": "full_numbers",
          "aaSorting": [[0,'desc'], [1,'asc']]
        });
      });
    }});
  }});

  $(function() {
    app.run();
  });
});
