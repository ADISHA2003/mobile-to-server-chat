import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Define server host and port
HOST = '0.0.0.0'  # Allows connections from any network interface
HTTP_PORT = 8080  # HTTP server port
SOCKET_PORT = 65432  # Arbitrary non-privileged port

# Define server class for handling HTTP requests
class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Serve a simple HTML page with a text input field
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
            <!DOCTYPE html>
<html>
<head>
    <title>mobile-to-server-chat</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f0f0f0;
        }
        .container {
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            text-align: center;
            color: #333;
        }
        form {
            text-align: center;
            margin-top: 20px;
        }
        input[type="text"] {
            width: 80%;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        input[type="submit"] {
            width: 80%;
            padding: 10px;
            background-color: #007bff;
            color: #fff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        input[type="submit"]:hover {
            background-color: #0056b3;
        }
        .success-message {
            color: #28a745;
            text-align: center;
            margin-top: 10px;
        }
        @media (max-width: 768px) {
            .container {
                max-width: 90%;
                margin: 20px auto;
            }
            input[type="text"], input[type="submit"] {
                width: 100%;
            }
        }
    </style>
    <script>
        function sendMessage() {
            var message = document.getElementById("message").value;
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/");
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    console.log("Message sent successfully");
                    document.getElementById("message").value = ""; // Clear input field
                    document.getElementById("success-message").innerText = "Message sent successfully!";
                    setTimeout(function () {
                        document.getElementById("success-message").innerText = ""; // Clear success message after 3 seconds
                    }, 3000);
                }
            };
            xhr.send("message=" + message);
            return false; // Prevent default form submission
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>Type through your mobile phone</h1>
        <form onsubmit="return sendMessage()">
            <input type="text" id="message" name="message" placeholder="Type your message here">
            <br>
            <input type="submit" value="Send">
            <div class="success-message" id="success-message"></div>
        </form>
    </div>
</body>
</html>

            """
            self.wfile.write(html.encode())

    def do_POST(self):
        # Receive data from the client (mobile phone)
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = parse_qs(post_data)
        if 'message' in params:
            message = params['message'][0]
            print('Received:', message)
            self.send_response(200)
            self.end_headers()
        else:
            self.send_error(400, 'Bad Request: "message" parameter not found')

# Define function to handle socket connections
def handle_socket():
    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Bind the socket to the host and port
        server_socket.bind((HOST, SOCKET_PORT))
        # Listen for incoming connections
        server_socket.listen()
        print("Socket server listening on port", SOCKET_PORT)
        while True:
            # Accept a client connection
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

# Define function to handle client connections
def handle_client(conn, addr):
    print('Connected by', addr)
    while True:
        # Receive data from the client
        data = conn.recv(1024)
        if not data:
            break
        # Decode data and print it
        print('Received from {}: {}'.format(addr, data.decode()))
    conn.close()

# Start HTTP server in a separate thread
http_thread = threading.Thread(target=HTTPServer((HOST, HTTP_PORT), HTTPRequestHandler).serve_forever)
http_thread.daemon = True
http_thread.start()

# Start socket server
socket_thread = threading.Thread(target=handle_socket)
socket_thread.daemon = True
socket_thread.start()

print("HTTP server listening on port", HTTP_PORT)

# Keep the main thread alive
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Exiting...")
