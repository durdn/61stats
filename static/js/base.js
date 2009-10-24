$(document).ready(function() {
  spinning_gif = '<img src="/static/img/89.gif" />';
  if (!window.console) window.console = {};
  if (!window.console.log) window.console.log = function() {};
  //data table connect
  $('#bumps-table').dataTable();

  //sammy routes definitions
  app = $.sammy(function() { with(this) {
    get('#/user/:username/:reload', function() { with(this) {
      $("#progress-bar").progressBar(0).show();
      $.get('/collect/' + params['username'] + '/1', function (data) {
    	var response = eval('(' + data + ')');
    	page = parseInt(response['page']);
    	numpages = parseInt(response['numpages']);
    	if (response['result'] == 'OK') {
            var percentage = Math.floor(100 * parseInt(page) / parseInt(numpages));
            $("#progress-bar").progressBar(percentage);
            for (i=page+1;i<=numpages;i++) {
              $.get('/collect/' + params['username'] + '/' + i, function (data) {
                var res = eval('(' + data + ')');
               	page = res['page'];
                numpages = res['numpages'];
                if (res['result'] == 'OK') {
                  var percentage = Math.floor(100 * parseInt(page) / parseInt(numpages));
                  $("#progress-bar").progressBar(percentage);
                }
              });
            }
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
