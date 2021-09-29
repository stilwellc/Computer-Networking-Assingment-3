from socket import *

def smtp_client(port=1025, mailserver='127.0.0.1'):
    msg = "\r\n My message"
    endmsg = "\r\n.\r\n"
    email = "cns9383@nyu.edu \r\n"

    # Choose a mail server (e.g. Google mail server) if you want to verify the script beyond GradeScope

    # Create socket called clientSocket and establish a TCP connection with mailserver and port
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((mailserver,port))

    recv = clientSocket.recv(1024).decode()

    # Send HELO command and print server response.
    heloCommand = 'HELO Alice\r\n'
    clientSocket.send(heloCommand.encode())
    recv

    # Send MAIL FROM command and print server response.
    mailFrom = "MAIL FROM: " + email
    clientSocket.send(mailFrom.encode())
    recv

    # Send RCPT TO command and print server response.
    rcptTo = "RCPT TO: " + email
    clientSocket.send(rcptTo.encode())
    recv
    
    # Send DATA command and print server response.
    data = "DATA \r\n"
    clientSocket.send(data.encode())
    recv
    
    # Send message data.
    messageSubject = "Subject: Test Test Test \r\n\r\n"
    clientSocket.send(messageSubject.encode())
    clientSocket.send(msg.encode())
    clientSocket.send(endmsg.encode())
    recv
    
    # Message ends with a single period.
    #TODO

    # Send QUIT command and get server response.
    quit = "QUIT \r\n"
    clientSocket.send(quit.encode())
    recv

if __name__ == '__main__':
    smtp_client(1025, '127.0.0.1')
