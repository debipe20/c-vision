import socket
import json
import datetime
import time

fileName = "map.json"

# Read a config file into a json object:
configFile = open("/nojournal/bin/mmitss-phase3-master-config.json", 'r')
config = (json.load(configFile))
configFile.close()

hostIp = config["HostIp"]
port = config["PortNumber"]["MessageTransceiver"]["MessageDecoder"]
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((hostIp,port))

priorityRequestGeneratorPort = config["PortNumber"]["PriorityRequestGeneratorServer"]
communicationInfo = (hostIp, priorityRequestGeneratorPort)
mapSendingTime = 0.0

while True:
    if time.time()-mapSendingTime >=1.0:
        f = open(fileName, 'r')
        data = f.read()
        s.sendto(data.encode(),communicationInfo)
        mapSendingTime = time.time()
        print("sent Map at time", time.time())

f.close()
s.close()