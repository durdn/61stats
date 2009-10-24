$(document).ready(function() {
  spinning_gif = '<img src="/static/img/89.gif" />';
  if (!window.console) window.console = {};
  if (!window.console.log) window.console.log = function() {};
  //data table connect
  $('#bumps-table').dataTable();

  //sammy routes definitions
  app = $.sammy(function() { with(this) {
    get('#/user/:username/:reload', function() { with(this) {
      //$('#reputation-bumps').html(spinning_gif);
      $.get('/user/' + params['username'] + '?reload=1', function (data) {
        $('#reputation-bumps').html(data).fadeIn();
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

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

var updater = {
    errorSleepTime: 500,
    cursor: null,

    poll: function() {
	var args = {"_xsrf": getCookie("_xsrf")};
	if (updater.cursor) args.cursor = updater.cursor;
	$.ajax({url: "/user/durdn?reload=1", type: "GET", dataType: "text",
		data: $.param(args), success: updater.onSuccess,
		error: updater.onError});
    },

    onSuccess: function(response) {
	try {
	    updater.newMessages(eval("(" + response + ")"));
	} catch (e) {
	    updater.onError();
	    return;
	}
	updater.errorSleepTime = 500;
	window.setTimeout(updater.poll, 0);
    },

    onError: function(response) {
	updater.errorSleepTime *= 2;
	console.log("Poll error; sleeping for", updater.errorSleepTime, "ms");
	window.setTimeout(updater.poll, updater.errorSleepTime);
    },

    newMessages: function(response) {
	if (!response.messages) return;
	updater.cursor = response.cursor;
	var messages = response.messages;
	updater.cursor = messages[messages.length - 1].id;
	console.log(messages.length, "new messages, cursor:", updater.cursor);
	for (var i = 0; i < messages.length; i++) {
	    updater.showMessage(messages[i]);
	}
    },

    showMessage: function(message) {
	var existing = $("#m" + message.id);
	if (existing.length > 0) return;
	var node = $(message.html);
	node.hide();
	$("#inbox").append(node);
	node.slideDown();
    }
};
