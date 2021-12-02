from socket import *
import os
import sys
import struct
import time
import select
import binascii
 
ICMP_ECHO_REQUEST = 8
ICMP_HEADER_FORMAT = "!bbHHh"  
IP_HEADER_FORMAT = "!BBHHHBBHII"
ICMP_TIME_FORMAT = "d"  # d=double
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 1
# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise
 
def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0
 
    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2
 
    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff
 
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def read_icmp_header(raw: bytes) -> dict:
    icmp_header_keys = ('type', 'code', 'checksum', 'id', 'seq')
    return dict(zip(icmp_header_keys, struct.unpack(ICMP_HEADER_FORMAT, raw)))

def read_ip_header(raw: bytes) -> dict:
    def stringify_ip(ip: int) -> str:
        return ".".join(str(ip >> offset & 0xff) for offset in (24, 16, 8, 0))  # str(ipaddress.ip_address(ip))

    ip_header_keys = ('version', 'tos', 'len', 'id', 'flags', 'ttl', 'protocol', 'checksum', 'src_addr', 'dest_addr')
    ip_header = dict(zip(ip_header_keys, struct.unpack(IP_HEADER_FORMAT, raw)))
    ip_header['src_addr'] = stringify_ip(ip_header['src_addr'])
    ip_header['dest_addr'] = stringify_ip(ip_header['dest_addr'])
    return ip_header

def build_packet():
    #Fill in start
    # In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our
    # packet to be sent was made, secondly the checksum was appended to the header and
    # then finally the complete packet was sent to the destination.
 
    # Make the header in a similar way to the ping exercise.
    # Append checksum to the header.
 
    # Don’t send the packet yet , just return the final packet in this function.
    myChecksum = 0
    ID = os.getpid() & 0xFFFF  # Return the current process i
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header

    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network  byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    #Fill in end
 
    # So the function ending should look like this
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    packet = header + data
    return packet
 
def get_route(hostname):
    timeLeft = TIMEOUT
    tracelist1 = [] #This is your list to use when iterating through each trace 
    tracelist2 = [] #This is your list to contain all traces
 
    for ttl in range(1,MAX_HOPS):
        for tries in range(TRIES):
            destAddr = gethostbyname(hostname)
 
            #Fill in start
            # Make a raw socket named mySocket
            icmp = getprotobyname("icmp")

            # SOCK_RAW is a powerful socket type. For more details:   http://sockraw.org/papers/sock_raw
            mySocket = socket(AF_INET, SOCK_RAW, icmp)
            #Fill in end
 
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t= time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []: # Timeout
                    tracelist1.append("* * * Request timed out.")
                    #Fill in start
                    #You should add the list above to your all traces list
                    tracelist1 = []
                    tracelist1.append(str(ttl))
                    tracelist1.append('*')
                    tracelist1.append('Request timed out')
                    tracelist2.append(tracelist1)
                    #Fill in end
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    tracelist1.append("* * * Request timed out.")
                    #Fill in start
                    #You should add the list above to your all traces list
                    tracelist1= []
                    tracelist1.append(str(ttl))
                    tracelist1.append('*')
                    tracelist1.append('Request timed out')
                    tracelist2.append(tracelist1)
                    #Fill in end
            except timeout:
                continue
 
            else:
                #Fill in start
                #Fetch the icmp type from the IP packet
                ip_header_slice = slice(0, struct.calcsize(IP_HEADER_FORMAT))  # [0:20]
                ip_header_raw = recvPacket[ip_header_slice]
                ip_header = read_ip_header(ip_header_raw)
                # print(f"debug: IP Header {ip_header}")
                icmp_header_slice = slice(ip_header_slice.stop, ip_header_slice.stop + struct.calcsize(ICMP_HEADER_FORMAT))  # [20:28]
                icmp_header_raw, icmp_payload_raw = recvPacket[icmp_header_slice], recvPacket[icmp_header_slice.stop:]
                icmp_header = read_icmp_header(icmp_header_raw)
                # print(f"debug: ICMP Header: {icmp_header}")
                types = icmp_header['type']
                #Fill in end
                try: #try to fetch the hostname
                    #Fill in start
                    host = gethostbyaddr(ip_header['src_addr'])[0]
                    #Fill in end
                except herror:   #if the host does not provide a hostname
                    #Fill in start
                    host ='hostname not returnable'
                    #Fill in end
 
                if types == 11:
                    bytes = struct.calcsize("d")
                    try:
                        timeSent = struct.unpack("d", recvPacket[56:56 +
                    bytes])[0]
                    except:
                        # handle cases where router does not return original data
                        timeSent = time.time()
                    #Fill in start
                    #You should add your responses to your lists here
                    tracelist1 = []
                    tracelist1.append(str(ttl))
                    delayMs = int((timeReceived - timeSent) * 1000)
                    tracelist1.append(f"{delayMs}ms")
                    tracelist1.append(ip_header['src_addr'])
                    tracelist1.append(host)
                    tracelist2.append(tracelist1)
                    #Fill in end
                elif types == 3:
                    bytes = struct.calcsize("d")
                    try:
                        timeSent = struct.unpack("d", recvPacket[56:56 + bytes])[0]
                    except:
                        # handle missing ICMP data
                        timeSent = time.time()
                    #Fill in start
                    tracelist1 = []
                    tracelist1.append(str(ttl))
                    delayMs = int((timeReceived - timeSent) * 1000)
                    tracelist1.append(f"{delayMs}ms")
                    tracelist1.append(ip_header['src_addr'])
                    tracelist1.append(host)
                    tracelist2.append(tracelist1)
                    #You should add your responses to your lists here 
                    #Fill in end
                elif types == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #Fill in start
                    #You should add your responses to your lists here and return your list if your destination IP is met
                    tracelist1 = []
                    tracelist1.append(str(ttl))
                    delayMs = int((timeReceived - timeSent) * 1000)
                    tracelist1.append(f"{delayMs}ms")
                    tracelist1.append(ip_header['src_addr'])
                    tracelist1.append(host)
                    tracelist2.append(tracelist1)
                    # We can stop now we reached the host
                    # print the results
                    if (len(tracelist1) == 4):
                        print(f"{tracelist1[0]:>8}    {tracelist1[1]:4} {tracelist1[2]:16} {tracelist1[3]}")
                    else:
                        print(f"{tracelist1[0]:>8}    {tracelist1[1]:4} {tracelist1[2]}")
                    return(tracelist2)
                    #Fill in end
                else:
                    #Fill in start
                    #If there is an exception/error to your if statements, you should append that to your list here
                    tracelist1 = []
                    tracelist1.append(str(ttl))
                    tracelist1.append('*')
                    tracelist1.append('Unexpected ICMP type')
                    tracelist2.append(tracelist1)
                    #Fill in end
                break
            finally:
                mySocket.close()
        # print the results
        if (len(tracelist1) == 4):
            print(f"{tracelist1[0]:>8}    {tracelist1[1]:4} {tracelist1[2]:16} {tracelist1[3]}")
        else:
            print(f"{tracelist1[0]:>8}    {tracelist1[1]:4} {tracelist1[2]}")
    return(tracelist2)
