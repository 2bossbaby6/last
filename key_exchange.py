import random

def diffie_hellman(p, g):
    # Step 1: Generate private keys for Alice and Bob
    a = random.randint(1, p-1)  # Alice's private key
    b = random.randint(1, p-1)  # Bob's private key

    # Step 2: Calculate public keys
    A = pow(g, a, p)  # Alice's public key
    B = pow(g, b, p)  # Bob's public key

    # Step 3: Exchange public keys and compute the shared secret
    shared_secret_alice = pow(B, a, p)
    shared_secret_bob = pow(A, b, p)

    # Ensure the shared secrets match
    assert shared_secret_alice == shared_secret_bob, "Shared secrets do not match!"

    return {
        "p": p,
        "g": g,
        "alice_private_key": a,
        "bob_private_key": b,
        "alice_public_key": A,
        "bob_public_key": B,
        "shared_secret": shared_secret_alice
    }

# Example parameters (small values for simplicity)
p = 23  # A prime number
g = 5   # A primitive root modulo p

result = diffie_hellman(p, g)

print(f"Prime number (p): {result['p']}")
print(f"Primitive root (g): {result['g']}")
print(f"Alice's private key: {result['alice_private_key']}")
print(f"Bob's private key: {result['bob_private_key']}")
print(f"Alice's public key: {result['alice_public_key']}")
print(f"Bob's public key: {result['bob_public_key']}")
print(f"Shared secret: {result['shared_secret']}")