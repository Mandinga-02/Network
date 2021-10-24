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
# Model class
class Result(BaseModel):
    name : str
    num_networks: int
    num_hosts: int
    first_add: str
    last_add: str



@app.get("/", tags=["home"])
async def root(message:dict):
    response = {"hello": "is online"}
    return response


# Function to calculate the ip class address
# Get detail
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
db = []
# Display results
@app.post("/ipcalc/")
async def ipcalc(add:dict):
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
@app.post('/subnet/')
async def subnet(add: dict) -> dict:
    data1 = add.get("address")
    data2 = add.get("mask")

    """Get the CIDR of the network"""
    cidr = data1.split(".")
    # del cidr[len(cidr) - 1]
    #  Prefix
    prefix = "/" + str(subnet_bits(data2))
    # subnet_bits the mask to binary
    cidr.append(prefix)
    res = ".".join(cidr)
    """ Calculate the available host per subnet"""
    # formula: 2^n - 2 where n is (32 - network bits).
    hosts_per_subnet = power(32-subnet_bits(data2)) - 2

    # num_subnets
    num_subnets = power(num_subnet(data2))
    """Valid subnets"""
    subs = []
    [subs.append(data1) for _ in range(num_subnets)]
    n = power(32-subnet_bits(data2))
    m = 0
    l = [list(i) for i in subs]
    for x in l:
        del x[len(x) - 1]
        x.append(str(m))
        m += n

    valid_subnets = [''.join(x) for x in l]

    """"broadcast addresses"""
    #  To get the broadcast, we convert the host bits of the network address to 1's
    # requirement:
        # cidr
        # network add
    cid = subnet_bits(data2)

    to_bin = " ".join([bin(int(x)) for x in data1.split(".")])
    # while i < len(cid):




    broadcast_add = [''.join(x) for x in l]
    # display result in JSON format.
    return {"address_cidr": res, "num_subnets": num_subnets,
    "addressable_hosts_per_subnet": hosts_per_subnet,"valid_subnets":valid_subnets,
    "broadcast_addresses":broadcast_add, "first_addresses":"N/A",
    "last_addresses":"N/A",}, cid, len(to_bin)
    # return cidr, p


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
