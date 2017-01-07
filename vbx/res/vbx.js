var buttons = document.getElementById('buttons').childNodes;
var conversations = [];
var contacts = document.getElementById('contacts');
var phone = document.getElementById('phone');
var status = document.getElementById('status');

var contact = {};

var xhr = function(method, resource, data, callback) {
	var req = new XMLHttpRequest();

	req.responseType = 'json';

	req.addEventListener('load', function(ev) {
		callback(req.response);
	});

	req.open(method, resource);

	req.send(data);
};

var load = function() {
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
};

var unload = function() {
	// mark offline
	xhr('post', '/browser', {'online': false});
};

var open = function(number) {
	if (document.getElementById(number) !== null) {
		// create new chat block
	}

	// bring it forward
	select(number);
};

var click = function(key) {
};

var call = function(number) {
	// call number
	select('phone');
};

var select = function(id) {
	if (id === 'phone') {
		// simply display phone
		phone.style.display = 'block';
	}
	else if (id === 'toggle') {
		// display or hide phone
		phone.style.display = phone.style.display == 'none' ? 'block' : 'none';
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
		document.getElementById(id).style.display = 'block';
	}

	// disable all buttons
	buttons.forEach(function(element) {
		element.style.classList.remove('active');
	});

	// mark respective button as active
	document.getElementById('button_' + id).style.classList.add('active');
};

window.addEventHandler('load', load);
window.addEventHandler('unload', unload);
