from fastapi import FastAPI, Body
from pydantic import BaseModel
import json
# The app router

# GET func
app = FastAPI()

# dictionary to hold the values of classes
classes={
    'A':{

    'network_bits':7,

    'host_bits':24,
    "first_address": "1.0.0.0",
    "last_address": "126.0.0.0"


    },

    'B':{

    'network_bits':14,

    'host_bits':16,
    "first_address": "128.0.0.0",
    "last_address": "191.255.255.255"

    },

    'C':{

    'network_bits':21,

    'host_bits':8,
    "first_address": "192.0.1.0",
    "last_address": "223.255.255.0"


    },

    'D':{

    'network_bits':'N/A',

    'host_bits':'N/A',
    "first_address": "224.0.0.0",
    "last_address": "239.255.255.255"

    },

    'E':{

    'network_bits':'N/A',

    'host_bits':'N/A',
    "first_address": "240.0.0.0",
    "last_address": "255.255.255.254"


    },

}


@app.get("/", tags=["home"])
async def root(message:dict):
    response = {"hello": "is online"}
    return response


# IP Calculator using the getDetails function

@app.post("/ipcalc/", tags=["ipcalc"])
async def ipcalc(add:dict):
    """    The ipcalc function takes a JSON object as input and return a JSON format response
                The ipcalc uses a helper function getDetails(), which takes a string as an input and return the appropriate class information such as the number of networks, number of hosts, first and last addresses of the ip address in JSON format response. E.g: Input={"address": "192.168.10.0",}
                Response => {
                  "class": "B",
                  "num_networks": 16384,
                  "num_hosts": 65536,
                  "first_address": "128.0.0.0",
                  "last_address": "191.255.255.255"
                }
            """
    #  Extract data
    data = add.get("address")
    # Calculate and display results
    return getDetails(data)
    # return data

# Subnet enpoint
"""json
{
    "address": "192.168.10.0",
    "mask": "255.255.255.192"
}

"""
@app.post('/subnet/',tags=["subnet calculator"])
async def subnet(add: dict) -> dict:
    """The Subnet funtion takes a JSON item,
    parses the data into address and mask. 
    It then calculates the CIDR (the suffix),
    the host per subnet using the host formula
    (2^n - 2, where n 32 - (the number of network bits)),
    number of subnets (2^bits borrowed), range of valid
    subnets, IP ranges from first to last addresses.

    E.g: Input = {
        "address": "192.168.10.0",
        "mask": "255.255.255.192"
    }
    Response => {
      "address_cidr": "192.168.10.0./26",
      "num_subnets": 4,
      "addressable_hosts_per_subnet": 62,
      "valid_subnets": [
        "192.168.10.0",
        "192.168.10.64",
        "192.168.10.128",
        "192.168.10.192"
      ],
      "broadcast_addresses": "N/A",
      "first_addresses": [
        "192.168.10.1",
        "192.168.10.65",
        "192.168.10.129",
        "192.168.10.193"
      ],
      "last_addresses": [
        "192.168.10.62",
        "192.168.10.126",
        "192.168.10.190",
        "192.168.10.254"
      ]
    }
    """
    # Parse the JSON
    data1 = add.get("address")
    data2 = add.get("mask")

    """Get the CIDR of the network"""
    cidr = data1.split(".")
    # convert the mask to binary
    suffix = "/" + str(subnet_bits(data2))
    cidr.append(suffix)
    res = ".".join(cidr)

    """ Calculate the available host per subnet"""
    # formula: 2^n - 2 where n is (32 - network bits).
    hosts_per_subnet = power(32-subnet_bits(data2)) - 2

    # number of subnets that can be created from the IP
    num_subnets = power(num_subnet(data2))

    """Valid subnets"""
    subs = []
    [subs.append(data1) for _ in range(num_subnets)]
    n = power(32-subnet_bits(data2))
    start = 0
    lst = [list(i) for i in subs]  # temporary list to store each ip converted to a list
    for x in lst:
        del x[len(x) - 1]
        x.append(str(start))
        start += n
    valid_subnets = [''.join(x) for x in lst] #  Valid subnets

    """"broadcast addresses"""

    """First addresses"""
    start = 1
    f_addr = [list(i) for i in subs]
    for x in f_addr:
        del x[len(x) - 1]
        x.append(str(start))
        start += n

    first_add = ["".join(x) for x in f_addr] #List of first addresses

    """Last addresses"""
    start = hosts_per_subnet
    l_addr = [list(i) for i in subs]
    for x in l_addr:
        del x[len(x) - 1]
        x.append(str(start))
        start += n

    last_add = ["".join(x) for x in l_addr] #List of last addresses
    # display result in JSON format.
    return {"address_cidr": res, "num_subnets": num_subnets,
    "addressable_hosts_per_subnet": hosts_per_subnet,"valid_subnets":valid_subnets,
    "broadcast_addresses":"N/A", "first_addresses":first_add,
    "last_addresses":last_add,}

"""Supernet calc"""
# {
#     "addresses":["205.100.0.0","205.100.1.0",
#     "205.100.2.0","205.100.3.0"]
# }
# Default class C mask is 255.255.255.0
# Therefore new subnet mask is 255.255.252.0
@app.post("/supernet/", tags=["supernet calculator"])
async def supernet(addr:dict):
    """The Supernet function takes @parameter dict (JSON item)
    and return a JSON format response. This function calculates
    the CIDR and the new subnet mask of class C IP addresses.
    E.g: Input={
         "addresses":["205.100.0.0","205.100.1.0",
         "205.100.2.0","205.100.3.0"]
    }
    Response =>{
      "address": [
        "205.100.0./22",
        "205.100.1./22",
        "205.100.2./22",
        "205.100.3./22"
      ],
      "mask": "255.255.252.0"
    }"""

    add = addr.get("addresses")
    cidr = add[len(add) -1]

    # Add cidr suffix to each IPs in the list
    lst = [list(i) for i in add]
    for i in lst:
        del i[len(i) -1]
        i.append("/22")

    new_subnet_mask = ["".join(i) for i in lst]
    class_C_mask = "255.255.252.0"
    return {
    "address":new_subnet_mask,
    "mask":class_C_mask}


# Function to calculate the ip class address details
def getDetails(string):
    res = string.split(".")  #Parse the JSON
    if int(res[0]) in range(0, 127):
        # For class A networks
        class_ = "A"
        n = classes['A']['network_bits'] #network number
        num_networks =  power(n)
        num_hosts = power(classes['A']['host_bits'])
        first_address = classes['A']['first_address']
        # return num_networks
        last_address = classes['A']['last_address']

        # For class B networks
    elif int(res[0]) in range(128, 193):
        # Verify for class
        class_ = "B"
        n = int(classes['B']['network_bits']) #network number
        num_networks =  power(n)
        num_hosts = power(classes['B']['host_bits'])
        first_address = classes['B']['first_address']
        # return num_networks
        last_address = classes['B']['last_address']

        # For class C networks
    elif int(res[0]) in range(224,240):
        # Verify for class
        class_ = "C"
        n = classes['C']['network_bits'] #network number
        num_networks =  power(n)
        num_hosts = power(classes['C']['host_bits'])
        first_address = classes['C']['first_address']
        # return num_networks
        last_address = classes['C']['last_address']

        # For class D networks
    elif int(res[0]) in range(224,239):
        # Verify for class
        class_ = "D"
        n = int(classes['D']['network_bits']) #network number
        num_networks =  classes['D']['network_bits']
        num_hosts = classes['D']['host_bits']
        first_address = classes['D']['first_address']
        # return num_networks
        last_address = classes['D']['last_address']
        # items = Result

    elif int(res[0]) in range(240, 255):
        # Verify for class
        class_ = "E"
        n = classes['E']['network_bits'] #network number
        num_networks =  classes['E']['network_bits']
        num_hosts = classes['E']['host_bits']
        first_address = classes['E']['first_address']
        # return num_networks
        last_address = classes['E']['last_address']
        # items = Result
    else:
        # Verify for class
        class_ = "N/A"
        n = classes #network number
        num_networks = 'N/A'
        num_hosts = 'N/A'
        first_address = 'N/A'
        # return num_networks
        last_address ='N/A'
        # items = Result
    items = {"class": class_, "num_networks": num_networks, "num_hosts": num_hosts
    , "first_address": first_address, "last_address": last_address,}

    return items


# Calculate the power
def power(n):
    return 2 ** n


# convert mask to binary
def subnet_bits(n):

    n = n.split(".")
    res = " ".join([bin(int(x)) for x in n])
    num = res.count("1")
    return num


def num_subnet(n):

    n = n.split(".")
    res = [bin(int(x)) for x in n]
    num = res[-1].count("1")
    return num
