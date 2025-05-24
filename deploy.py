from web3 import Web3
from dotenv import load_dotenv
from solcx import compile_standard, install_solc
import json
import os

def compile_and_deploy_contract():
    print("Compiling and deploying the smart contract...")
    
    # Load environment variables
    load_dotenv()
    
    # Install solidity compiler
    print("Installing solc...")
    install_solc("0.8.0")
    
    # Read the smart contract
    with open("contracts/CertificateVerifier.sol", "r") as file:
        certificate_verifier_file = file.read()
    
    # Compile the smart contract
    print("Compiling smart contract...")
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"CertificateVerifier.sol": {"content": certificate_verifier_file}},
            "settings": {
                "outputSelection": {
                    "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                }
            },
        },
        solc_version="0.8.0",
    )
    
    # Save the compiled contract
    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/CertificateVerifier.json", "w") as file:
        json.dump(compiled_sol, file)
    
    # Extract the contract data
    contract_data = compiled_sol["contracts"]["CertificateVerifier.sol"]["CertificateVerifier"]
    abi = contract_data["abi"]
    bytecode = contract_data["evm"]["bytecode"]["object"]
    
    # Connect to Ethereum network
    print("Connecting to Ethereum network...")
    infura_url = os.getenv("INFURA_URL")
    if not infura_url:
        print("INFURA_URL not found in environment variables!")
        return None, None
    
    w3 = Web3(Web3.HTTPProvider(infura_url))
    
    # Check if connected
    if not w3.is_connected():
        print("Failed to connect to Ethereum network!")
        return None, None
    
    print(f"Connected to network. Chain ID: {w3.eth.chain_id}")
    
    # Get the account details
    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        print("PRIVATE_KEY not found in environment variables!")
        return None, None
    
    account = w3.eth.account.from_key(private_key)
    
    print(f"Deploying from account: {account.address}")
    print(f"Account balance: {w3.eth.get_balance(account.address) / 10**18} ETH")
    
    # Create the contract
    CertificateVerifier = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Get the nonce
    nonce = w3.eth.get_transaction_count(account.address)
    
    # Estimate gas
    try:
        gas_estimate = CertificateVerifier.constructor().estimate_gas({'from': account.address})
        print(f"Estimated gas: {gas_estimate}")
    except Exception as e:
        print(f"Gas estimation failed: {e}")
        gas_estimate = 3000000  # fallback
    
    # Build the transaction
    transaction = CertificateVerifier.constructor().build_transaction(
        {
            "chainId": w3.eth.chain_id,
            "gas": gas_estimate + 100000,  # Add buffer
            "gasPrice": w3.eth.gas_price,
            "from": account.address,
            "nonce": nonce,
        }
    )
    
    print(f"Transaction details:")
    print(f"  Gas: {transaction['gas']}")
    print(f"  Gas Price: {transaction['gasPrice']}")
    print(f"  Total Cost: {(transaction['gas'] * transaction['gasPrice']) / 10**18} ETH")
    
    # Sign the transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    
    # Send the transaction
    print("Deploying contract...")
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"Transaction hash: {tx_hash.hex()}")
    
    # Wait for transaction receipt
    print("Waiting for transaction receipt...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
    
    if tx_receipt.status == 1:
        print(f"✅ Contract deployed successfully at address: {tx_receipt.contractAddress}")
        
        # Save the contract address and ABI to a file
        contract_info = {
            "address": tx_receipt.contractAddress,
            "abi": abi,
            "network": "sepolia" if w3.eth.chain_id == 11155111 else "mainnet" if w3.eth.chain_id == 1 else "unknown",
            "deployment_tx": tx_hash.hex(),
            "deployment_block": tx_receipt.blockNumber,
            "gas_used": tx_receipt.gasUsed
        }
        
        with open("artifacts/contract_info.json", "w") as file:
            json.dump(contract_info, file, indent=2)
        
        print(f"📄 Contract info saved to artifacts/contract_info.json")
        print(f"⛽ Gas used: {tx_receipt.gasUsed}")
        
        return tx_receipt.contractAddress, abi
    else:
        print("❌ Contract deployment failed!")
        return None, None

def verify_deployment():
    """Verify that the deployed contract is working correctly"""
    try:
        # Load contract info
        with open("artifacts/contract_info.json", "r") as file:
            contract_info = json.load(file)
        
        # Connect to web3
        infura_url = os.getenv("INFURA_URL")
        w3 = Web3(Web3.HTTPProvider(infura_url))
        
        if not w3.is_connected():
            print("❌ Failed to connect for verification")
            return False
        
        # Create contract instance
        contract = w3.eth.contract(
            address=contract_info["address"], 
            abi=contract_info["abi"]
        )
        
        # Test a simple function call
        test_cert_id = "test-123"
        exists = contract.functions.certificateExists(test_cert_id).call()
        
        print(f"✅ Contract verification successful!")
        print(f"   Address: {contract_info['address']}")
        print(f"   Network: {contract_info.get('network', 'unknown')}")
        print(f"   Test function call successful: certificateExists('{test_cert_id}') = {exists}")
        
        return True
        
    except Exception as e:
        print(f"❌ Contract verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting smart contract deployment...")
    print("=" * 50)
    
    contract_address, abi = compile_and_deploy_contract()
    
    if contract_address:
        print("=" * 50)
        print("🎉 Deployment completed successfully!")
        print(f"📍 Contract Address: {contract_address}")
        print("📋 Features available:")
        print("   - Issue certificates with digital signatures")
        print("   - Store certificate hashes")
        print("   - Verify certificates and hashes")
        print("   - Revoke certificates")
        print("   - Validate signatures")
        
        print("\n🔍 Verifying deployment...")
        if verify_deployment():
            print("✅ All systems ready!")
        else:
            print("⚠️  Deployment successful but verification failed")
            
    else:
        print("=" * 50)
        print("❌ Deployment failed!")
        print("Please check your configuration and try again.")
        
    print("=" * 50)