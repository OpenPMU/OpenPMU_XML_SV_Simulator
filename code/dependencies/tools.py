"""
OpenPMU - Phasor Estimator
Copyright (C) 2021  www.OpenPMU.org

Licensed under GPLv3.  See __init__.py
"""

import socket
import psutil

def getLocalIP():
    
    family = socket.AF_INET
    
    ips = []
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == family:
                if snic.address.startswith("169.254"):   # Ignore 169.254.x.x
                    continue
                else:
                    ips.append(snic.address)
                    
    ips.sort()
    
    return(ips)


"""
The approach below works well until Python 3.7, but after that no wheel
seems to be available for netifaces, so a new approach using standard
libraries is now used.  Tested in Python 3.9 on Windows.
"""

# import netifaces

# def getLocalIP():
#     """
#     get the current ip address of local machine

#     :return: IP addresses in a list
#     """
#     try:
#         ips=[]
#         for i in netifaces.interfaces():
#             j=netifaces.ifaddresses(i)
#             if  netifaces.AF_INET in j.keys():
#                 for k in j[netifaces.AF_INET]:
#                     ips.append(k["addr"])
#         #ips=socket.gethostbyname_ex(socket.gethostname())[-1]
#     except:
#         return []
#     ips.sort()
#     return ips
