extends Node

var client: StreamPeerTCP
var connected = false
var hostname = "127.0.0.1"
var port = 65432

func _ready():
	client = StreamPeerTCP.new()
	connect_to_server()

func connect_to_server():
	print("Attempting to connect to Bridge Server...")
	var err = client.connect_to_host(hostname, port)
	if err == OK:
		connected = true
		print("Connected to Bridge Server!")
		# Send a handshake message
		send_message({"type": "handshake", "source": "godot_simulation"})
	else:
		print("Failed to connect. Error code: ", err)
		connected = false

func _process(delta):
	if not connected:
		return

	client.poll()
	var status = client.get_status()
	
	if status == StreamPeerTCP.STATUS_CONNECTED:
		var bytes_available = client.get_available_bytes()
		if bytes_available > 0:
			var data = client.get_utf8_string(bytes_available)
			print("Received from Bridge: ", data)
			process_command(data)
	elif status == StreamPeerTCP.STATUS_ERROR or status == StreamPeerTCP.STATUS_NONE:
		print("Connection lost.")
		connected = false

func send_message(data_dict):
	if connected:
		var json_str = JSON.stringify(data_dict)
		client.put_data(json_str.to_utf8_buffer())

func process_command(json_str):
	var json = JSON.new()
	var error = json.parse(json_str)
	if error == OK:
		var data = json.data
		if typeof(data) == TYPE_DICTIONARY:
			# Handle commands here
			if data.has("command"):
				match data.command:
					"spawn":
						print("Spawning object: ", data.get("name", "Unknown"))
						# Call your spawn function here
					"move_camera":
						print("Moving camera to: ", data.get("position", Vector3.ZERO))
	else:
		print("JSON Parse Error: ", json.get_error_message())
