from bluepy.btle import Scanner
 
scanner = Scanner()
devices = scanner.scan(10.0)
device_list = []

class Device:
    def __init__(self, addr, rssi, connectable):
        self.addr = addr
        self.rssi = rssi
        self.connectable = connectable
        
for device in devices:
    if device.rssi > -65:
        device_list.append(Device(device.addr, device.rssi, device.connectable))
        #print("DEV = {} RSSI = {} CONNECTABLE = {}".format(device.addr, device.rssi, device.connectable))
        #data = device.getScanData() 
        #print("DESC = {}".format(data))
for i in range(len(device_list)):
    print("DEV = {} // RSSI = {} // CONNECTABLE = {}".format(device_list[i].addr, device_list[i].rssi, device_list[i].connectable))