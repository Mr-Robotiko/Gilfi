#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// Compile: gcc rsa-module.c -o rsa-module
// Usage: ./rsa-module <plaintext>

typedef struct {
    
    int e;
    int d;
    long long n;

} RSAKeys;

int is_prime(int number) {

    if (number < 2) return 0;
    
    for (int i = 2; i * i <= number; i++) {
        if(number % i == 0) {
            return 0;
        }
    }

    return 1;
}

int gcd(int a, int b) {

    while(b != 0) {
        int temp = b;
        b = a % b;
        a = temp;
    }

    return a;
}

int get_mod_inv(int a, int b) {

    a = a % b;

    for(long long x = 1; x < b; x++) {
        if(((long long)a * x) % b == 1) {
            return (int)x;
        }
    }

    return -1; 
}

long long mod_pow(long long base, long long exp, long long mod) {
    
    long long result = 1;
    base %= mod;

    while (exp > 0) {
        if (exp % 2 == 1) {
            result = (result * base) % mod;
        }
        base = (base * base) % mod;
        exp /= 2;
    }

    return result;
}

RSAKeys key_generation() {

    RSAKeys keys;

    int p = 0, q = 0;

    srand(time(NULL));

    // 1) Generate prime numbers
    while (!is_prime(p))
        p = rand() % 50000 + 20000;

    while (!is_prime(q) || q == p)
        q = rand() % 50000 + 20000;

    printf("p = %d\n", p);
    printf("q = %d\n", q);

    // 2) n and phi
    long long n = (long long)p * q;
    long long phi = (long long)(p - 1) * (q - 1);

    printf("n = %lld\n", n);
    printf("phi = %lld\n", phi);

    // 3) find e
    int e = 0;
    while (e < 2 || gcd(e, phi) != 1)
        e = rand() % (phi - 2) + 2;

    // 4) d = e⁻¹ mod phi
    int d = get_mod_inv(e, phi);

    if (d == -1) {
        printf("Error: get_mod_inv returned no result.\n");
        exit(EXIT_FAILURE);
    }

    keys.e = e; // e, n -> public key
    keys.d = d; // d, n -> private key
    keys.n = n;

    return keys;
}

long long encrypt(long long M, int e, long long n) {
    // Cipher = Message^e mod n
    return mod_pow(M, e, n);
}

long long decrypt(long long C, int d, long long n) {
    // Message = Cipher^d mod n
    return mod_pow(C, d, n);
}

int main(int argc, char *argv[]) {
    // Argument given?
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <plaintext_number>\n", argv[0]);
        return EXIT_FAILURE;
    }

    // argv[1] -> long long
    long long plaintext;
    if (sscanf(argv[1], "%lld", &plaintext) != 1) {
        fprintf(stderr, "Error: Invalid number format for plaintext.\n");
        return EXIT_FAILURE;
    }
    
    printf("--- RSA Key Generation ---\n");
    RSAKeys keys = key_generation();
    printf("--------------------------\n");

    printf("\nPublic Key (e, n) = (%d, %lld)\n", keys.e, keys.n);
    printf("Private Key (d, n) = (%d, %lld)\n", keys.d, keys.n);
    
    // Is M < n?
    if (plaintext >= keys.n) {
        fprintf(stderr, "\nError: Plaintext M (%lld) must be less than n (%lld) for valid RSA operation.\n", plaintext, keys.n);
        return EXIT_FAILURE;
    }

    printf("\nOriginal message (M) = %lld\n", plaintext);

    // Encryption
    long long ciphertext = encrypt(plaintext, keys.e, keys.n);
    printf("Ciphertext (C) (%lld^%d mod %lld) = %lld\n", plaintext, keys.e, keys.n, ciphertext);

    // Decryption
    long long decrypted_message = decrypt(ciphertext, keys.d, keys.n);
    printf("Decrypted message (M') (%lld^%lld mod %lld) = %lld\n", ciphertext, keys.d, keys.n, decrypted_message);

    return 0;   
}