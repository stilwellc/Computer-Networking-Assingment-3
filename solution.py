from socket import *
import os
import sys
import struct
import time
import select
import binascii
from statistics import stdev
# Should use stdev

ICMP_ECHO_REQUEST = 8
ICMP_ECHO_RESPONSE = 0
ICMP_HEADER_FORMAT = "!bbHHh"  
IP_HEADER_FORMAT = "!BBHHHBBHII"
ICMP_TIME_FORMAT = "d"  # d=double

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
    """Get information from raw ICMP header data.
    Args:
        raw: Bytes. Raw data of ICMP header.
    Returns:
        A map contains the infos from the raw header.
    """
    icmp_header_keys = ('type', 'code', 'checksum', 'id', 'seq')
    return dict(zip(icmp_header_keys, struct.unpack(ICMP_HEADER_FORMAT, raw)))

def read_ip_header(raw: bytes) -> dict:
    """Get information from raw IP header data.
    Args:
        raw: Bytes. Raw data of IP header.
    Returns:
        A map contains the infos from the raw header.
    """
    def stringify_ip(ip: int) -> str:
        return ".".join(str(ip >> offset & 0xff) for offset in (24, 16, 8, 0))  # str(ipaddress.ip_address(ip))

    ip_header_keys = ('version', 'tos', 'len', 'id', 'flags', 'ttl', 'protocol', 'checksum', 'src_addr', 'dest_addr')
    ip_header = dict(zip(ip_header_keys, struct.unpack(IP_HEADER_FORMAT, raw)))
    ip_header['src_addr'] = stringify_ip(ip_header['src_addr'])
    ip_header['dest_addr'] = stringify_ip(ip_header['dest_addr'])
    return ip_header

def receiveOnePing(mySocket, ID, timeout, destAddr):
   timeLeft = timeout
   time_sent = time.time()

   while 1:
       startedSelect = time.time()
       whatReady = select.select([mySocket], [], [], timeLeft)
       howLongInSelect = (time.time() - startedSelect)
       if whatReady[0] == []:  # Timeout
           return "Request timed out."

       timeReceived = time.time()
       recPacket, addr = mySocket.recvfrom(1024)

       # Fill in start

       # Fetch the IP and ICMP header from the IP packet
       # IP header needed for TTL and address info

       ip_header_slice = slice(0, struct.calcsize(IP_HEADER_FORMAT))  # [0:20]
       ip_header_raw = recPacket[ip_header_slice]
       ip_header = read_ip_header(ip_header_raw)
       # print("debug: IP Header", ip_header)
       icmp_header_slice = slice(ip_header_slice.stop, ip_header_slice.stop + struct.calcsize(ICMP_HEADER_FORMAT))  # [20:28]
       icmp_header_raw, icmp_payload_raw = recPacket[icmp_header_slice], recPacket[icmp_header_slice.stop:]
       icmp_header = read_icmp_header(icmp_header_raw)
       # print("debug: ICMP Header: ", icmp_header)
       if icmp_header['type'] == ICMP_ECHO_REQUEST:  # filters out the ECHO_REQUEST itself.
           # print("ECHO_REQUEST received. Packet filtered out.")
           continue
       if icmp_header['type'] == ICMP_ECHO_RESPONSE:
           timeSent = struct.unpack(ICMP_TIME_FORMAT, icmp_payload_raw[0:struct.calcsize(ICMP_TIME_FORMAT)])[0]
           delayMs = (timeReceived - timeSent) * 1000 # in milliseconds
           print(f"Reply from {ip_header['src_addr']}: bytes={ip_header['len']} time={delayMs}ms TTL={ip_header['ttl']}")
           return delayMs
       # Fill in end
       timeLeft = timeLeft - howLongInSelect
       if timeLeft <= 0:
           return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
   # Header is type (8), code (8), checksum (16), id (16), sequence (16)

   myChecksum = 0
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
   packet = header + data

   mySocket.sendto(packet, (destAddr, 1))  # AF_INET address must be tuple, not str


   # Both LISTS and TUPLES consist of a number of objects
   # which can be referenced by their position number within the object.

def doOnePing(destAddr, timeout):
   icmp = getprotobyname("icmp")


   # SOCK_RAW is a powerful socket type. For more details:   http://sockraw.org/papers/sock_raw
   mySocket = socket(AF_INET, SOCK_RAW, icmp)

   myID = os.getpid() & 0xFFFF  # Return the current process i
   sendOnePing(mySocket, destAddr, myID)
   delay = receiveOnePing(mySocket, myID, timeout, destAddr)
   mySocket.close()
   return delay

def ping(host, timeout=1):
   # timeout=1 means: If one second goes by without a reply from the server,      # the client assumes that either the client's ping or the server's pong is lost
   try:
      dest = gethostbyname(host)
   except:
      # Unknown host
      print("ping: Name or service not known:", host)
      return(['0', '0.0', '0', '0.0'])
   print("Pinging " + dest + " using Python:")
   print("")
   packet_resp = []
   # Calculate vars values and return them
   #  vars = [str(round(packet_min, 2)), str(round(packet_avg, 2)), str(round(packet_max, 2)),str(round(stdev(stdev_var), 2))]
   # Send ping requests to a server separated by approximately one second
   for i in range(0,4):
       delay = doOnePing(dest, timeout)
       # print(delay)
       if (delay != "Request timed out."):
           packet_resp.append(delay) # save the response time
       else:
           print(delay)
       time.sleep(1)  # one second
   # Calculate vars
   packet_resp.sort() # sort the list to get min / max
   packet_min = 0
   packet_max = 0
   packet_avg = 0.0
   stdev_var = [ 0.0, 0.0 ]
   packet_loss = 0.0
   # print("debug: packet_resp: ",packet_resp)
   if (packet_resp):
       # at least one packet came back
       packet_min = packet_resp[0]
       packet_max = packet_resp[len(packet_resp) - 1]
       packet_avg = sum(packet_resp) / len(packet_resp)
       stdev_var = packet_resp
   vars = [str(round(packet_min, 2)), str(round(packet_avg, 2)), str(round(packet_max, 2)),str(round(stdev(stdev_var), 2))]
   print("")
   print("---",host,"ping statistics ---")
   packet_loss = ((4 - len(packet_resp)) / 4) * 100
   print(f"4 packets transmitted, {len(packet_resp)} received, {packet_loss}% packet loss")
   print(f"round-trip min/avg/max/stddev = {vars[0]}/{vars[1]}/{vars[2]}/{vars[3]}")
   # print("debug: vars:",vars)
   return vars

if __name__ == '__main__':
   ping("google.co.il")
