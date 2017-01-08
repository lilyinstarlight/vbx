var buttons = [];
var main = null;
var conversations = [];
var contacts = null;
var phone = null;
var last = null;
var status = null;

var contact = {};

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
	status = document.getElementById('status');

	contact = {};

	// setup select
	phone.style.display = 'none';

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
				call(key);
			});
			button_message.addEventListener('click', function(ev) {
				open(key);
			});

			li.appendChild(span_name);
			li.appendChild(span_number);
			li.appendChild(button_call);
			li.appendChild(button_message);

			contacts.appendChild(li);
		});
	});

	// setup callbacks

	// mark online
	xhr('post', '/browser', {'online': true});

	// select nothing
	select(null);

	// show body
	document.body.style.display = 'flex';
};

var unload = function() {
	// mark offline
	xhr('post', '/browser', {'online': false});
};

var open = function(number) {
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
		button.addEventListener('click', function(ev) { select(number) });
	}

	// bring it forward
	select(number);
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

	if (status.innerText === 'Connecting...' || status.innerText === 'Connected') {
		if (key === 'hangup') {
		}
		else {
			sendDTMF();
		}
	}
	else {
		if (key === 'dial') {
			call(status.innerText);
		}
		else {
			status.innerText += key;
		}
	}
};

var call = function(number) {
	// call number
	select('phone');
};

var hangup = function() {
	// close phone
	select(last);
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
		phone.style.display = 'initial';
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
			document.getElementById(id).style.display = 'initial';
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
