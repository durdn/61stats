function collect(username,page, numpages) {
	if (page == numpages) {
        var percentage = Math.floor(100 * parseInt(page) / parseInt(numpages));
        $("#progress-bar").progressBar(percentage);
        $("#progress-bar").fadeOut();
        $.get('/user/' + username, function (data) {
          $('#reputation-bumps').html(data).fadeIn();
          $('#bumps-table').dataTable({
            "bSort": true,
            "bStateSave": true,
            "sPaginationType": "full_numbers",
            "aaSorting": [[0,'desc'], [1,'asc']]
          });
        });
		return;
	} else {
      $.get('/collect/' + username + '/' + page, function (data) {
    	var response = eval('(' + data + ')');
    	page = parseInt(response['page']);
    	numpages = parseInt(response['numpages']);
    	if (response['result'] == 'OK') {
            var percentage = Math.floor(100 * parseInt(page) / parseInt(numpages));
            $("#progress-bar").progressBar(percentage);
            collect(username,page+1,numpages);
    	}
      });
	}	
}

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
      collect(params['username'],1,-1);
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
