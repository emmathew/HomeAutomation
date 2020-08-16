import subprocess
from utilities import Logger

WPA_SUPPLICANT_CONF_BACKUP_PATH = "/home/pi/MHomeAutomation/wpa_supplicant_backup.conf"
WPA_SUPPLICANT_CONF_ACTUAL_PATH = "/etc/wpa_supplicant/wpa_supplicant.conf"
WIFI_INTERFACE                  = "wlan0"
MHA_ACCESS_POINT_PREFIX         = "MHA_Client_"

class WifiAp:
    def __init__(self, mac, ssid):
        self.macAddr = mac
        self.ssid = ssid


def getMacAddr (wifiAp):
    return wifiAp.macAddr

def getSsid (wifiAp):
    return wifiAp.ssid

def findMhaDevices():
    mhaDevicesInfo = []
    availableWifiNetworks = scanWifi()
    for wifi in availableWifiNetworks:
        #print(str(wifi.ssid) + ":->" + str(wifi.macAddr) + "\n")
        if MHA_ACCESS_POINT_PREFIX in wifi.ssid:
            mhaDevicesInfo.append(wifi)
    return mhaDevicesInfo

def scanWifi():
    availableWifiNetworks = []
    shcmd = 'sudo iwlist ' + WIFI_INTERFACE + ' scan'
    response = subprocess.run(shcmd.split(' '), capture_output=True, timeout=30)
    if response.returncode == 0:            
        output = response.stdout.decode("utf-8").split('\n')
        macAddr = ''
        ssid = ''
        for line in output:
            if 'Address' in line:
                macAddr = line.split('Address:')[-1][1:-1]
            if 'ESSID' in line:
                ssid = line.split(':')[-1][1:-1]

            if macAddr != '' and ssid != '':
                availableWifiNetworks.append(WifiAp(macAddr,ssid))
                macAddr = ''
                ssid = ''
                
    else:
        Logger.log(Logger.LogLevel.error, "Wifi Scaning failed")
    return availableWifiNetworks
        

def connectToWifi (ssid, macaddr):
    shutil.copy(WPA_SUPPLICANT_CONF_BACKUP_PATH, WPA_SUPPLICANT_CONF_ACTUAL_PATH)
    newStrToAddToFile = '\nnetwork={\n\tssid="'+ssid+'"\n\tkey_mgmt=NONE\n\tscan_ssid=1\n}'
    
    if os.path.exists(WPA_SUPPLICANT_CONF_ACTUAL_PATH) == False:
        println("Error Connecting to Wifi. File Not present")
        errorCode = 1
        return errorCode

    f = open(WPA_SUPPLICANT_CONF_ACTUAL_PATH,"a+")
    f.write(newStrToAddToFile)
    f.close()

    shcmd = 'wpa_cli -i wlan0 reconfigure'
    response = subprocess.run(shcmd.split(' '), capture_output=True, timeout=30)
    if response.returncode != 0:
        println("Error reconfiguring wireless interface")
        errorCode = 2
        return errorCode

    # Check if Wifi connected
    shcmd = 'ifconfig wlan0'
    response = subprocess.run(shcmd.split(' '), capture_output=True, timeout=30)
    if response.returncode != 0:
        println("Error validating wifi connection.")
        errorCode = 2
        return errorCode
    output = response.stdout.decode("utf-8").split('\n')
    ipaddr='192.168.4.1'
    for line in output:
        if 'inet ' in line:
            # Connected
            println("Wifi Connected")
            return 0
    println("Could not verify wifi connection")
    errorCode = 3
    return errorCode

