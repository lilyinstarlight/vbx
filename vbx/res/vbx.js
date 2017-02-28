var nav = null;
var buttons = [];
var main = null;
var conversations = [];
var record = null;
var contacts = null;
var phone = null;
var message = null;
var message_number = null;
var last = null;
var state = 'idle';
var statusline = null;

var contact = {};

var number = null;

var token = null;
var connection = null;
var incoming = null;

var recordTime = new Date();
var messageTime = new Date();

var xhr = function(method, resource, data, callback) {
	var req = new XMLHttpRequest();

	req.responseType = 'json';

	req.addEventListener('load', function(ev) {
		callback === undefined || callback(req.response);
	});

	req.open(method, resource);
	if (data === undefined) {
		req.send();
	}
	else {
		req.setRequestHeader('Content-Type', 'application/json');
		req.send(JSON.stringify(data));
	}
};

var mktime = function(date) {
	var time = '';

	time += date.getFullYear();
	time += '-';
	time += ('0' + (date.getMonth() + 1)).slice(-2);
	time += '-';
	time += ('0' + date.getDate()).slice(-2);
	time += ' ';
	time += ('0' + date.getHours()).slice(-2);
	time += ':';
	time += ('0' + date.getMinutes()).slice(-2);

	return time;
};

var notify = function(message) {
	if (Notification.permission === 'granted')
		var notification = new Notification(message);
};

if (Notification.permission !== 'granted' && Notification.permission !== 'denied')
	Notification.requestPermission();

var load = function() {
	// get elements
	nav = document.getElementById('nav');
	buttons = [document.getElementById('button_history'), document.getElementById('button_contacts'), document.getElementById('button_message'), document.getElementById('button_phone')];
	main = document.getElementById('main');
	conversations = [];
	record = document.getElementById('history');
	contacts = document.getElementById('contacts');
	phone = document.getElementById('phone');
	message = document.getElementById('message');
	message_number = document.getElementById('message_number');
	statusline = document.getElementById('status');

	contact = {};

	// load contacts
	xhr('get', '/contacts/', undefined, function(response) {
		contact = response;

		var tbody = contacts.children[0].children[0];

		Object.keys(contact).forEach(function(key) {
			var span_name = document.createElement('span');
			var span_number = document.createElement('span');
			var button_message = document.createElement('button');
			var button_call = document.createElement('button');

			span_name.innerText = contact[key];
			span_number.innerText = key;

			button_message.innerText = 'Message';
			button_call.innerText = 'Call';

			button_message.addEventListener('click', function(ev) {
				window.open(key);
			});
			button_call.addEventListener('click', function(ev) {
				window.call(key);
			});

			var tr = document.createElement('tr');

			var td_name = document.createElement('td');
			var td_number = document.createElement('td');
			var td_message = document.createElement('td');
			var td_call = document.createElement('td');

			td_name.appendChild(span_name);
			td_number.appendChild(span_number);
			td_message.appendChild(button_message);
			td_call.appendChild(button_call);

			tr.appendChild(td_name);
			tr.appendChild(td_number);
			tr.appendChild(td_message);
			tr.appendChild(td_call);

			tbody.appendChild(tr);
		});
	});

	// setup callbacks
	xhr('get', '/browser', undefined, function(data) {
		// get number
		number = data.number;

		// get token
		token = data.token;

		// setup Twilio.Device
		Twilio.Device.setup(token);

		Twilio.Device.connect(function(conn) {
			state = 'connected';
			statusline.innerText = 'Connected.';
		});

		Twilio.Device.disconnect(function(conn) {
			state = 'idle';
			statusline.innerText = 'Dial a Number';
		});

		Twilio.Device.incoming(function(conn) {
			state = 'incoming';

			incoming = conn;

			// get from name
			from = conn.parameters.From;

			if (from in contact)
				from = contact[from];

			statusline.innerText = 'Incoming Call From ' + from;

			if (!document.hasFocus())
				window.notify(statusline.innerText);

			// open phone
			select('phone');
		});

		Twilio.Device.cancel(function(conn) {
			state = 'idle';
			statusline.innerText = 'Dial a Number';

			// close phone
			select(last);
		});

		Twilio.Device.offline(function(device) {
			// get another token
			xhr('get', '/browser', undefined, function(data) {
				// get token
				token = data.token;

				// setup Twilio.Device
				Twilio.Device.setup(token);
			});
		});

		// setup history callbacks
		var recordUpdate = function() {
			// ignore costly history update if not focused
			if (record.style.display === '') {
				var tbody = record.children[0].children[0];

				var write = function(tbody, data) {
					if (data.direction === 'inbound')
						var number = data.from;
					else
						var number = data.to;

					var other = number in contact ? contact[number] : number;

					var span_other = document.createElement('span');
					var span_data = document.createElement('span');
					var time = document.createElement('time');
					var button_message = document.createElement('button');
					var button_call = document.createElement('button');

					span_other.innerText = other;

					if ('status' in data) {
						var message = '';

						if (data.direction === 'inbound')
							message += 'Incoming';
						else
							message += 'Outgoing';

						message += ' Call:';

						if (data.status === 'queued')
							message += ' Queued';
						else if (data.status === 'ringing')
							message += ' Ringing';
						else if (data.status === 'in-progress')
							message += ' In Progress';
						else if (data.status === 'canceled')
							message += ' Canceled';
						else if (data.status === 'completed')
							message += ' Completed (' + data.duration + ' seconds)';
						else if (data.status === 'failed')
							message += ' Failed';
						else if (data.status === 'busy')
							message += ' Busy';
						else if (data.status === 'no-answer')
							message += ' No Answer';
						else
							message += ' Unknown';

						span_data.innerText = message;
					}
					else if ('body' in data) {
						var message = '';

						if (data.direction === 'inbound')
							message += 'Incoming';
						else
							message += 'Outgoing';

						message += ' Message:';

						message += ' ' + data.body;

						if (data.media_url !== null)
							message += ' [media]';

						span_data.innerText = message;
					}
					else {
						span_data.innerText = data;
					}


					time.innerText = window.mktime(new Date(data.date));

					button_message.innerText = 'Message';
					button_call.innerText = 'Call';

					button_message.addEventListener('click', function(ev) {
						window.open(number);
					});
					button_call.addEventListener('click', function(ev) {
						window.call(number);
					});

					var tr = document.createElement('tr');

					tr.id = 'history_' + data.sid;

					var td_other = document.createElement('td');
					var td_data = document.createElement('td');
					var td_time = document.createElement('td');
					var td_message = document.createElement('td');
					var td_call = document.createElement('td');

					td_other.appendChild(span_other);
					td_data.appendChild(span_data);
					td_time.appendChild(time);
					td_message.appendChild(button_message);
					td_call.appendChild(button_call);

					tr.appendChild(td_other);
					tr.appendChild(td_data);
					tr.appendChild(td_time);
					tr.appendChild(td_message);
					tr.appendChild(td_call);

					tbody.appendChild(tr);
				};

				var currentTime = recordTime;
				var current = recordTime.toISOString();
				var nextTime = new Date();

				// load call history
				xhr('get', '/calls/?start_time_after=' + current, undefined, function(calls) {
					xhr('get', '/msgs/?date_sent_after=' + current, undefined, function(msgs) {
						// get all history elements
						var entries = calls.concat(msgs);

						// filter out extra entries
						entries.filter(function(entry) {
							return (entry.to !== 'client:vbx' && entry.from !== 'client:vbx') && (entry.direction === 'inbound' || entry.direction === 'outbound-api');
						});

						// sort by date
						entries.sort(function(left, right) {
							return new Date(left.date) - new Date(right.date);
						});

						// generate elements
						entries.forEach(function(data) {
							if (document.getElementById('history_' + data.sid) !== null)
								write(tbody, data);
						});

						// scroll history down
						record.scrollTop = 2147483646;
					});
				});

				recordTime = nextTime;
			}

			setTimeout(recordUpdate, 2000);
		};

		// initiate history updates
		recordUpdate();

		// setup message callbacks
		var messageUpdate = function() {
			var currentTime = messageTime;
			var current = messageTime.toISOString();
			var nextTime = new Date();

			xhr('get', '/msgs/?date_sent_after=' + current + '&to=' + number, undefined, function(data) {
				data.forEach(function(message) {
					// prevent double writes
					if (document.getElementById(message.sid) === null) {
						if (!document.hasFocus())
							window.notify((message.from in contact ? contact[message.from] : message.from) + ': ' + message.body);

						window.open(message.from, message);
					}
				});
			});

			xhr('get', '/msgs/?date_sent_after=' + current + '&from=' + number, undefined, function(data) {
				data.forEach(function(message) {
					// prevent double writes
					if (document.getElementById(message.sid) === null)
						window.open(message.to, message);
				});
			});

			messageTime = nextTime;

			setTimeout(messageUpdate, 2000);
		};

		// initiate message updates
		messageUpdate();

		// setup ping callbacks
		var pingUpdate = function() {
			xhr('post', '/browser', {});

			setTimeout(pingUpdate, 5000);
		};

		// initiate ping updates
		pingUpdate();
	});

	// select nothing
	select(null);

	// show body
	document.body.style.display = 'flex';
};

var open = function(number, message) {
	var show = function(number) {
		// create new chat block
		var chat = document.createElement('div');
		chat.id = number;
		chat.classList.add('chat');
		chat.style.display = 'none';

		var container = document.createElement('div');

		var input = document.createElement('input');
		input.type = 'text';
		input.placeholder = 'Enter Message Here...';
		input.addEventListener('keyup', function(ev) {
			if (ev.keyCode === 13) {
				ev.preventDefault();
				xhr('post', '/msg', {'to': number, 'body': input.value});
				input.value = '';
			}
		});

		chat.appendChild(container);
		chat.appendChild(input);

		main.appendChild(chat);
		conversations.push(chat);

		// create button
		var button_container = document.createElement('div');
		button_container.id = 'nav_' + number;

		var button = document.createElement('button');
		button.id = 'button_' + number;
		if (number in contact)
			button.innerText = contact[number];
		else
			button.innerText = number;
		button.addEventListener('click', function(ev) { window.select(number) });

		buttons.push(button);

		var close = document.createElement('button');
		close.classList.add('close');
		close.innerText = '×';
		close.addEventListener('click', function(ev) { window.close(number) });

		button_container.appendChild(button);
		button_container.appendChild(close);

		nav.insertBefore(button_container, nav.firstChild);

		return container;
	}

	var write = function(container, number, message) {
		// create chat bubble
		var div = document.createElement('div');
		div.id = message.sid;

		// set class based on whether this was sent or receieved
		if (message.from === number)
			div.classList.add('me');
		else
			div.classList.add('you');

		// format time
		var time = document.createElement('time');
		time.innerText = window.mktime(new Date(message.date));

		// add body
		var p = document.createElement('p');
		p.innerText = message.body;

		// join time and body into message
		div.appendChild(time);
		div.appendChild(p);

		// add media if necessary
		if (message.media_url !== null) {
			var embed = document.createElement('embed');
			embed.src = message.media_url;
			embed.type = message.media_type;

			embed.addEventListener('load', function(ev) {
				// scroll chat down
				container.scrollTop = 2147483646;
			});

			div.appendChild(embed);
		}

		// add message to chat window
		container.appendChild(div);

		// scroll chat down
		container.scrollTop = 2147483646;
	}

	if (document.getElementById(number) === null) {
		// show number
		var container = show(number);

		// bring chat forward
		select(number);

		// load chat
		xhr('get', '/msgs/?to=' + number, undefined, function(data) {
			xhr('get', '/msgs/?from=' + number, undefined, function(dataInner) {
				// get all messages
				var messages = data.concat(dataInner);

				// sort by date
				messages.sort(function(left, right) {
					return new Date(left.date) - new Date(right.date);
				});

				// generate elements
				messages.forEach(function(message) {
					write(container, number, message);
				});
			});
		});
	}
	else {
		// get container
		var container = document.getElementById(number).children[0];

		// bring chat forward
		select(number);

		// load given message
		if (message !== undefined)
			write(container, number, message);
	}
};

var close = function(number) {
	var chat = document.getElementById(number);

	if (chat === null)
		return;

	// remove chat block
	main.removeChild(chat);
	conversations.splice(conversations.indexOf(chat), 1);

	var container = document.getElementById('nav_' + number);

	if (container === null)
		return;

	// remove button
	nav.removeChild(container);
	buttons.splice(buttons.indexOf(container.children[0]), 1);

	// bring last thing forward
	select(last);
};

var click = function(key) {
	if (key === 'message') {
		window.open(message_number.value);
		message_number.value = '';

		return;
	}

	if (state === 'connecting' || state === 'connected') {
		if (key === 'hangup') {
			hangup();
		}
		else if (key === 'dial') {
			// do nothing
		}
		else {
			connection.sendDigits(key);
		}
	}
	else if (state === 'idle') {
		if (key === 'hangup') {
			// do nothing
		}
		else if (key === 'dial') {
			// do nothing
		}
		else {
			// convert first 0 to a +
			if (key === '0')
				key = '+';

			statusline.innerText = key;
		}

		state = 'dialing';
	}
	else if (state === 'dialing') {
		if (key === 'dial') {
			call(statusline.innerText);
		}
		else if (key === 'hangup') {
			statusline.innerText = 'Dial a Number...';

			state = 'idle';
		}
		else {
			statusline.innerText += key;
		}
	}
	else if (state === 'incoming') {
		if (key === 'dial') {
			incoming.accept();

			connection = incoming;
		}
		else if (key === 'hangup') {
			incoming.reject();
		}

		state = 'connected';
		status.innerText = 'Connected.';
	}
};

var call = function(number) {
	// update state
	state = 'connecting';

	// create connection
	connection = Twilio.Device.connect({'To': number});

	// call number
	select('phone');
};

var hangup = function() {
	// close phone
	select(last);

	// disconnect line
	Twilio.Device.disconnectAll();
};

var select = function(id) {
	if (id === 'toggle_phone') {
		if (phone.style.display === 'none')
			// behave as though phone were selected
			id = 'phone';
		else
			// behave as though last were selected
			id = last;
	}
	else if (id === 'toggle_message') {
		if (message.style.display === 'none')
			// behave as though message were selected
			id = 'message';
		else
			// behave as though last were selected
			id = last;
	}

	if (id === 'phone') {
		// simply display phone
		phone.style.display = '';
		message.style.display = 'none';
	}
	else if (id === 'message') {
		// display message
		message.style.display = '';
		phone.style.display = 'none';
	}
	else {
		// close all conversations
		conversations.forEach(function(element) {
			element.style.display = 'none';
		});

		// close phone and contacts
		record.style.display = 'none';
		contacts.style.display = 'none';
		message.style.display = 'none';
		phone.style.display = 'none';

		// display requested section
		if (id !== null) {
			var target = document.getElementById(id);
			if (target !== null)
				target.style.display = '';
			else
				id = null;
		}
	}

	// disable all buttons
	buttons.forEach(function(element) {
		element.classList.remove('active');
	});

	// mark respective button as active
	if (id !== null)
		document.getElementById('button_' + id).classList.add('active');

	if (id !== 'phone' && id !== 'message')
		last = id;

	if (id === 'history')
		record.focus();
};

window.addEventListener('load', load);
