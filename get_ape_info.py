from web3 import Web3
from web3.providers.rpc import HTTPProvider
import requests
import json

bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
contract_address = Web3.to_checksum_address(bayc_address)

# You will need the ABI to connect to the contract
# The file 'abi.json' has the ABI for the bored ape contract
# In general, you can get contract ABIs from etherscan
# https://api.etherscan.io/api?module=contract&action=getabi&address=0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D
with open('ape_abi.json', 'r') as f:
    abi = json.load(f)

############################
# Connect to an Ethereum node
api_url = "https://eth-mainnet.g.alchemy.com/v2/pN0drT7H3rHSPkxHJECaw"  # YOU WILL NEED TO PROVIDE THE URL OF AN ETHEREUM NODE
provider = HTTPProvider(api_url)
web3 = Web3(provider)

contract = web3.eth.contract(address=contract_address, abi=abi)

def _ipfs_to_urls(ipfs_uri):
    # Example: ipfs://Qm.../1
    path = ipfs_uri.replace("ipfs://", "", 1)
    return [
        f"https://ipfs.io/ipfs/{path}",
        f"https://gateway.pinata.cloud/ipfs/{path}",
        f"https://cloudflare-ipfs.com/ipfs/{path}",
    ]


def _fetch_json_from_ipfs(ipfs_uri):
    urls = _ipfs_to_urls(ipfs_uri)

    for url in urls:
        try:
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass

    raise Exception(f"Could not fetch metadata from IPFS: {ipfs_uri}")


def get_ape_info(ape_id):
    assert isinstance(ape_id, int), f"{ape_id} is not an int"
    assert 0 <= ape_id, f"{ape_id} must be at least 0"
    assert 9999 >= ape_id, f"{ape_id} must be less than 10,000"

    data = {'owner': "", 'image': "", 'eyes': ""}

    # YOUR CODE HERE
    owner = contract.functions.ownerOf(ape_id).call()
    token_uri = contract.functions.tokenURI(ape_id).call()
    metadata = _fetch_json_from_ipfs(token_uri)
    image = metadata.get("image", "")
    eyes = ""

    for attr in metadata.get("attributes", []):
        if attr.get("trait_type") == "Eyes":
            eyes = attr.get("value", "")
            break

    data["owner"] = owner
    data["image"] = image
    data["eyes"] = eyes

    assert isinstance(data, dict), f'get_ape_info{ape_id} should return a dict'
    assert all([a in data.keys() for a in
                ['owner', 'image', 'eyes']]), f"return value should include the keys 'owner','image' and 'eyes'"
    return data
