# Author: Yehonatan Thee
# giy
# The implementation is include validation, communication with server and for checking, some files that the user can ask
# from the server.
import socket
import os

IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 0.1
DEFAULT_URL = r'index.html'
ROOT = r'C:\Users\Thee\PycharmProjects\SocketHTTP'
BASIC_RESPONSE = 'HTTP/1.1 200 OK\r\n'
REDIRECTION_DICTIONERY = {'imgs/favicon.ico': 'HTTP/1.1 302 Moved Temporarily\r\nLoection:favicon.ico\r\n\r\n ',
                          'test.PDF': 'HTTP/1.1 403 Forbidden\r\nStatus Code: 403 Forbidden\r\n'
                          }


def get_file_data(filename):
    """ Get data from file """
    if os.path.isfile(filename):
        data = open(filename, "rb")
        data = data.read()
        if filename[-3:] != 'jpg' and filename[-3:] != 'ico':
            return data.decode()
        else:
            return data
    else:
        return "ERROR"


def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client"""

    if resource == '':
        url = DEFAULT_URL
    else:
        url = resource

    if url in REDIRECTION_DICTIONERY:
        http_response = REDIRECTION_DICTIONERY[url]
        client_socket.send(http_response.encode())
    else:
        http_header = None
        if url[-4:] == 'html' or url[-3:] == 'txt':
            http_header = BASIC_RESPONSE + 'Content-Type: text/html; charset=utf-8\r\n'
        elif url[-3:] == 'jpg':
            http_header = BASIC_RESPONSE + 'Content-Type: image/jpeg\r\n'
        elif url[-3:] == 'ico':
            http_header = BASIC_RESPONSE + 'Content-Type: image / x - icon\r\n'
        elif url[-2:] == 'js':
            http_header = BASIC_RESPONSE + 'Content-Type: text/javascript; charset=UTF-8\r\n'
        elif url[-3:] == 'css':
            http_header = BASIC_RESPONSE + 'Content-Type: text/css\r\n'

        if http_header and os.path.isfile(ROOT + "\\" + url):
            http_header = http_header + "Content-Length: " + str(os.path.getsize(ROOT + "\\" + url)) + "\r\n\r\n"
            data = get_file_data(ROOT + "\\" + url)
            if data == "ERROR":
                http_response = "HTTP/1.1 404 Not Found\r\nStatus Code: 404 Not Found\r\n"
                client_socket.send(http_response.encode())
            else:
                http_response = http_header + str(data)
                if url[-3:] != 'jpg' and url[-3:] != 'ico':
                    client_socket.send(http_response.encode())
                else:
                    client_socket.send(http_header.encode() + data)
        else:
            http_response = "HTTP/1.1 500 Internal Server Error\r\nStatus Code: 500 Internal Server Error\r\n\r\n"
            client_socket.send(http_response.encode())


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL
    """
    # We want to check the header, so take the first line and check
    check = request.split('\n', 1)[0]
    # The first line at the request is the validation header
    if check[0:5] == 'GET /' and check[-10:] == ' HTTP/1.1\r':
        request = check[5:-10]
        return True, request
    else:
        return False, "ERROR"


def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """

    print('Client connected')
    while True:
        client_request = client_socket.recv(1024).decode()
        print(client_request.split('\n', 1)[0])
        valid_http, resource = validate_http_request(client_request)
        if valid_http:
            print('Got a valid HTTP request')
            handle_client_request(resource, client_socket)
        else:
            print('Error: Not a valid HTTP request')
            if client_request == "":
                break
    client_socket.send("HTTP/1.1 500 Internal Server Error\r\n\r\n")
    print('Closing connection')
    client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(PORT))

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)
        try:
            handle_client(client_socket)
        except socket.timeout:
            print("timeout exception is caught")


if __name__ == "__main__":
    # Call the main handler function
    main()
