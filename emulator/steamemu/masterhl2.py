import threading, logging, struct, binascii, time, atexit, socket, ipaddress, os.path, ast
import os
import config
import utilities
import steamemu.logger
import globalvars
import serverlist_utilities
from serverlist_utilities import send_heartbeat, remove_from_dir

class masterhl2(threading.Thread):

    def __init__(self, host, port):
        #threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_type = "MasterHL2SRV"
        self.server_info = {
                    'ip_address': globalvars.serverip,
                    'port': int(self.port),
                    'server_type': self.server_type,
                    'timestamp': int(time.time())
                }
        # Register the cleanup function using atexit
        #atexit.register(remove_from_dir(globalvars.serverip, int(self.port), self.server_type))             
        thread2 = threading.Thread(target=self.heartbeat_thread)
        thread2.daemon = True
        thread2.start()
        
    def heartbeat_thread(self):       
        while True:
            send_heartbeat(self.server_info)
            time.sleep(1800) # 30 minutes
            
    def start(self):
        self.socket.bind((self.host, self.port))
        while True: #recieve a packet
            data, address = self.socket.recvfrom(1280) # Start a new thread to process each packet
            threading.Thread(target=self.process_packet, args=(data, address)).start()

    def process_packet(self, data, address):
        log = logging.getLogger("hl2mstr")
        clientid = str(address) + ": "
        log.info(clientid + "Connected to HL2 Master Server")
        log.debug(clientid + ("Received message: %s, from %s" % (data, address)))

        if data.startswith("1") :
            i = 0
            header = bytearray()
            header += b'\xFF\xFF\xFF\xFF\x66\x0A'
            while i < 1000 : #also change in command "b" and in globalvars
                if not isinstance(globalvars.hl2serverlist[i], int) :
                    print(globalvars.hl2serverlist[i])
                    trueip = globalvars.hl2serverlist[i][0].split('.')
                    trueip_int = map(int, trueip)
                    header += struct.pack('>BBBB', trueip_int[0], trueip_int[1], trueip_int[2], trueip_int[3])
                    try :
                        trueport_int_temp = int(globalvars.hl2serverlist[i][24])
                    except :
                        trueport_int_temp = 1
                    if not len(str(trueport_int_temp)) == 5 :
                        trueport_int = 27015
                    else :
                        trueport_int = trueport_int_temp
                    print(str(trueport_int))
                    header += struct.pack('>H', trueport_int)
                i += 1
            nullip = struct.pack('>BBBB', 0, 0, 0, 0)
            nullport = struct.pack('>H', 0)
            serversocket.sendto(header + nullip + nullport, address)
        elif data.startswith("q") :
            header = b'\xFF\xFF\xFF\xFF\x73\x0A'
            ipstr = str(address)
            ipstr1 = ipstr.split('\'')
            ipactual = ipstr1[1]
            portstr = ipstr1[2]
            portstr1 = portstr.split(' ')
            portstr2 = portstr1[1].split(')')
            portactual_temp = portstr2[0]
            if not str(len(portactual_temp)) == 5 :
                portactual = "27015"
            else :
                portactual = str(portactual_temp)
            registered = 0
            for server in globalvars.hl2serverlist :
                if len(str(server)) > 5 :
                    if server[0] == ipactual and (str(server[24]) == portactual or "27015" == portactual) :
                        log.info(clientid + "Already registered, sending challenge number %s" % str(server[4]))
                        challenge = struct.pack("I", int(server[4]))
                        registered = 1
                        break
            if registered == 0 :
                log.info(clientid + "Registering server, sending challenge number %s" % str(globalvars.hl2challengenum + 1))
                challenge = struct.pack("I", globalvars.hl2challengenum + 1)
                globalvars.hl2challengenum += 1
            serversocket.sendto(header + challenge, address)
        elif data.startswith("0") :
            serverdata1 = data.split('\n')
            #print(serverdata1)
            serverdata2 = serverdata1[1]
            #print(serverdata2)
            ipstr = str(address)
            ipstr1 = ipstr.split('\'')
            serverdata3 = ipstr1[1] + serverdata2
            #print(serverdata3)
            tempserverlist = serverdata3.split('\\')
            #print(tempserverlist)
            globalvars.hl2serverlist[int(tempserverlist[4])] = tempserverlist
            #print(tempserverlist[0])
            #print(tempserverlist[1])
            #print(tempserverlist[2])
            #print(tempserverlist[3])
            #print(tempserverlist[4])
            #print(tempserverlist[5])
            log.debug(clientid + "This Challenge: %s" % tempserverlist[4])
            log.debug(clientid + "Current Challenge: %s" % (globalvars.hl2challengenum))
        elif data.startswith("b") :
            ipstr = str(address)
            ipstr1 = ipstr.split('\'')
            ipactual = ipstr1[1]
            portstr = ipstr1[2]
            portstr1 = portstr.split(' ')
            portstr2 = portstr1[1].split(')')
            portactual_temp = portstr2[0]
            if not str(len(portactual_temp)) == 5 :
                portactual = "27015"
            else :
                portactual = str(portactual_temp)
            i = 0
            running = 0
            while i < 1000 :
                if not isinstance(globalvars.hl2serverlist[i], int) :
                    running += 1
                    #print(ipactual + ":" + portactual)
                    #print(type(ipactual))
                    #print(type(portactual))
                    #print(type(globalvars.hl2serverlist[i][0]))
                    #print(type(globalvars.hl2serverlist[i][24]))
                    #for server in globalvars.hl2serverlist :
                    #print(server)
                    if globalvars.hl2serverlist[i][0] == ipactual and (str(globalvars.hl2serverlist[i][24]) == portactual or "27015" == portactual) :
                        #print(type(globalvars.hl2serverlist[i]))
                        #print(type(i))
                        #print(type(globalvars.hl2serverlist))
                        #print(globalvars.hl2serverlist[i][0])
                        #print(str(globalvars.hl2serverlist[i][24]))
                        globalvars.hl2serverlist.pop(i)
                        log.info(clientid + "Unregistered server: %s:%s" % (ipactual, portactual))
                        running -= 1
                i += 1
            print("Running servers: %s" % str(running))
        else :
            print("UNKNOWN MASTER SERVER COMMAND")

        #self.socket.close()
        log.info (clientid + "Disconnected from HL2 Master Server")
