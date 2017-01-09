var buttons = [];
var main = null;
var conversations = [];
var contacts = null;
var phone = null;
var last = null;
var state = 'idle';
var statusline = null;

var contact = {};

var number = null;

var token = null;
var connection = null;
var incoming = null;

var last = new Date().toISOString();

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

var load = function() {
	// get elements
	buttons = document.getElementById('buttons').children;
	main = document.getElementById('main');
	conversations = [];
	contacts = document.getElementById('contacts');
	phone = document.getElementById('phone');
	statusline = document.getElementById('status');

	contact = {};

	// load contacts
	xhr('get', '/contacts/', undefined, function(response) {
		contact = response;

		Object.keys(contact).forEach(function(key) {
			var li = document.createElement('li');

			var span_name = document.createElement('span');
			var span_number = document.createElement('span');
			var button_call = document.createElement('button');
			var button_message = document.createElement('button');

			span_name.innerText = contact[key];
			span_number.innerText = key;

			button_call.innerText = 'Call';
			button_message.innerText = 'Message';

			button_call.addEventListener('click', function(ev) {
				window.call(key);
			});
			button_message.addEventListener('click', function(ev) {
				window.open(key);
			});

			li.appendChild(span_name);
			li.appendChild(span_number);
			li.appendChild(button_call);
			li.appendChild(button_message);

			contacts.appendChild(li);
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

		Twilio.Device.connect(function (conn) {
			state = 'connected';
			statusline.innerText = 'Connected.';
		});

		Twilio.Device.disconnect(function (conn) {
			state = 'idle';
			statusline.innerText = 'Dial a Number';
		});

		Twilio.Device.incoming(function (conn) {
			state = 'incoming';

			incoming = conn;

			// get from name
			from = conn.parameters.From;

			if (from in contact)
				from = contact[from];

			statusline.innerText = 'Incoming Call From ' + from;

			// open phone
			select('phone');
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

		// mark online
		xhr('post', '/browser', {'online': true});
	});

	// setup message callbacks
	var messageUpdate = function() {
		var current = last;
		var next = new Date().toISOString();

		xhr('get', '/msgs/?date_sent_after=' + current + '&to=' + number, undefined, function(data) {
			data.forEach(function(msg) {
				open(msg.from, current);
			});
		});

		xhr('get', '/msgs/?date_sent_after=' + current + '&from=' + number, undefined, function(data) {
			data.forEach(function(msg) {
				open(msg.to, current);
			});
		});

		last = next;

		setTimeout(messageUpdate, 1000);
	};

	// select nothing
	select(null);

	// show body
	document.body.style.display = 'flex';
};

var unload = function() {
	// mark offline
	xhr('post', '/browser', {'online': false});
};

var open = function(number, date) {
	if (document.getElementById(number) === null) {
		// create new chat block
		var chat = document.createElement('div');
		chat.id = number;
		chat.classList.add('chat');

		var container = document.createElement('div');

		var input = document.createElement('input');
		input.type = 'text';
		input.placeholder = 'Enter Message Here...';

		chat.appendChild(container);
		chat.appendChild(input);

		main.appendChild(chat);
		conversations.push(chat);

		// create button
		var button = document.createElement('button');
		button.id = 'button_' + number;
		button.addEventListener('click', function(ev) { window.select(number) });
	}

	base = '/msgs/?';

	if (date !== undefined)
		base += 'date_sent_after=' + date + '&';

	// load chat
	xhr('get', base + 'to=' + number, function(data) {
		xhr('get', base + 'from=' + number, function(dataInner) {
			// get all messages
			var messages = data.concat(dataInner);

			// sort by date
			messages.sort(function(left, right) {
				return new Date(right.date) - new Date(left.date);
			});

			// generate elements
			messages.forEach(function(message) {
				// create chat bubble
				var div = document.createElement('div');

				// set class based on whether this was sent or receieved
				if (message.from === number)
					div.classList.add('me');
				else
					div.classList.add('you');

				// get message time
				var date = new Date(message.date);

				// format time
				var time = document.createElement('time');
				time.innerText = '';
				time.innerText += date.getFullYear();
				time.innerText += ('0' + (date.Month() + 1)).slice(-2);
				time.innerText += ('0' + date.getDate()).slice(-2);
				time.innerText += ' ';
				time.innerText += ('0' + date.getHours()).slice(-2);
				time.innerText += ':';
				time.innerText += ('0' + date.getSeconds()).slice(-2);

				// add body
				var p = document.createElement('p');
				p.innerText = message.body;

				// join time and body into message
				div.appendChild(time);
				div.appendChild(p);

				// add message to chat window
				document.getElementById(number).children[0].appendChild(div);
			});

			// bring chat forward
			select(number);
		});
	});
};

var close = function(number) {
	if (conversations.indexOf(number) === -1)
		return;

	// remove chat block
	main.removeChild(conversations[number]);

	// bring last thing forward
	select(last);
};

var click = function(key) {
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
			statusline.innerText = key;
		}

		state = 'dialing';
	}
	else if (state === 'dialing') {
		if (key === 'dial') {
			call(statusline.innerText);
		}
		else if (key === 'hangup') {
			statusline.innerText = 'Dial a Number';

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
	if (id === 'toggle') {
		if (phone.style.display === 'none')
			// behave as though phone were selected
			id = 'phone';
		else
			// behave as though last were selected
			id = last;
	}

	if (id === 'phone') {
		// simply display phone
		phone.style.display = '';
	}
	else {
		// close all conversations
		conversations.forEach(function(element) {
			element.style.display = 'none';
		});

		// close phone and contacts
		contacts.style.display = 'none';
		phone.style.display = 'none';

		// display requested section
		if (id !== null)
			document.getElementById(id).style.display = '';
	}

	// disable all buttons
	for (var button = 0; button < buttons.length; button++)
		buttons[button].classList.remove('active');

	// mark respective button as active
	if (id !== null)
		document.getElementById('button_' + id).classList.add('active');

	if (id !== 'phone')
		last = id;
};

window.addEventListener('load', load);
window.addEventListener('unload', unload);
