from socket import *

def smtp_client(port=1025, mailserver='127.0.0.1'):
    msg = "\r\n My message"
    endmsg = "\r\n.\r\n"
    email = "cns9383@nyu.edu \r\n"

    # Choose a mail server (e.g. Google mail server) if you want to verify the script beyond GradeScope

    # Create socket called clientSocket and establish a TCP connection with mailserver and port
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(mailserver)

    recv = clientSocket.recv(1024).decode()
    print(recv)
    #if recv[:3] != '220':
        #print('220 reply not received from server.')

    # Send HELO command and print server response.
    heloCommand = 'HELO Alice\r\n'
    clientSocket.send(heloCommand.encode())
    recv1 = clientSocket.recv(1024).decode()
    #print(recv1)
    #if recv1[:3] != '250':
        #print('250 reply not received from server.')

    # Send MAIL FROM command and print server response.
    mailFrom = "MAIL FROM: " + email
    clientSocket.send(mailFrom.encode())
    recv2 = clientSocket.recv(1024).decode()

    #print("MAIL FROM server response: " + recv2)
    #if recv2[:3] != '250':
       # print('250 reply not received from server.')

    # Send RCPT TO command and print server response.
    rcptTo = "RCPT TO: " + email
    clientSocket.send(rcptTo.encode())
    recv3 = clientSocket.recv(1024).decode()

   # print("RCPT TO server response: " + recv3)
    #if recv3[:3] != '250':
       # print('250 reply not received from server.')

    # Send DATA command and print server response.
    data = "DATA \r\n"
    clientSocket.send(data.encode())
    recv4 = clientSocket.recv(1024).decode()

    #print("DATA server response: " + recv4)
    #if recv4[:3] != '250':
       # print('250 reply not received from server.')

    # Send message data.
    messageSubject = "Subject: Test Test Test \r\n\r\n"
    clientSocket.send(messageSubject.encode())
    clientSocket.send(msg.encode())
    clientSocket.send(endmsg.encode())

    recv5 = clientSocket.recv(1024).decode()
    #print("message body sent server response: " + recv5)
    #if recv4[:3] != '250':
       # print('250 reply not received from server.')

    # Message ends with a single period.
    #TODO

    # Send QUIT command and get server response.
    quit = "QUIT \r\n"
    clientSocket.send(quit.encode())
    recv7 = clientSocket.recv(1024).decode()

   # print("QUIT server response: " + recv7)
    #if recv7[:3] != '250':
       # print('250 reply not received from server.')


if __name__ == '__main__':
    smtp_client(1025, '127.0.0.1')
