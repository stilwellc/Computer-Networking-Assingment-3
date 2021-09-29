from socket import *

def smtp_client(port=1025, mailserver='127.0.0.1'):
    msg = "\r\n My message"
    endmsg = "\r\n.\r\n"
    email = "cns9383@nyu.edu \r\n"

    # Create socket called clientSocket and establish a TCP connection with mailserver and port
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((mailserver,port))

    # Send HELO command and print server response.
    heloCommand = 'HELO Alice\r\n'
    clientSocket.send(heloCommand.encode())
    clientSocket.recv(1024).decode()

    # Send MAIL FROM command and print server response.
    mailFrom = "MAIL FROM: " + email
    clientSocket.send(mailFrom.encode())
    clientSocket.recv(1024).decode()

    # Send RCPT TO command and print server response.
    rcptTo = "RCPT TO: " + email
    clientSocket.send(rcptTo.encode())
    clientSocket.recv(1024).decode()

    # Send DATA command and print server response.
    data = "DATA \r\n"
    clientSocket.send(data.encode())
    clientSocket.recv(1024).decode()

    # Send message data.
    messageSubject = "Subject: Test Test Test \r\n\r\n"
    clientSocket.send(messageSubject.encode())
    clientSocket.send(msg.encode())
    clientSocket.send(endmsg.encode())
    clientSocket.recv(1024).decode()

    # Send QUIT command and get server response.
    quit = "QUIT \r\n"
    clientSocket.send(quit.encode())
    clientSocket.recv(1024).decode()


if __name__ == '__main__':
    smtp_client(1025, '127.0.0.1')
