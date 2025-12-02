#include <assert.h>
#include <stdio.h>
#include "../rsa-module.c"

void test_is_prime() {
    assert(is_prime(2) == 1);
    assert(is_prime(17) == 1);
    assert(is_prime(18) == 0);
    assert(is_prime(1) == 0);
}

void test_gcd() {
    assert(gcd(10, 5) == 5);
    assert(gcd(17, 31) == 1);
    assert(gcd(81, 27) == 27);
}

void test_mod_inv_basic() {
    assert(get_mod_inv(3, 40) == 27);
    assert(get_mod_inv(7, 40) == 23);
}

void test_mod_inv_no_inverse() {
    assert(get_mod_inv(6, 15) == -1);
    assert(get_mod_inv(10, 20) == -1);
}

void test_mod_inv_edge_cases() {
    assert(get_mod_inv(1, 37) == 1);
    assert(get_mod_inv(0, 37) == -1);
    assert(get_mod_inv(5, 1) == -1);
}

void test_mod_inv_a_greater_than_b() {
    assert(get_mod_inv(45, 26) == get_mod_inv(45 % 26, 26));
    assert(get_mod_inv(100, 37) == get_mod_inv(100 % 37, 37));
}

void test_mod_inv_large_values() {
    int inv = get_mod_inv(65537, 3120);
    assert(inv == 2753);
}

void test_mod_pow() {
    assert(mod_pow(4, 13, 497) == 445);
    assert(mod_pow(2, 20, 17) == 16);
}

void test_encrypt_decrypt_small_numbers() {
    RSAKeys keys = key_generation();
    long long m = 12345 % keys.n;
    long long c = encrypt(m, keys.e, keys.n);
    long long m2 = decrypt(c, keys.d, keys.n);
    assert(m == m2);
}

void test_encrypt_decrypt_edge_case() {
    RSAKeys keys = key_generation();
    long long m = 1;
    long long c = encrypt(m, keys.e, keys.n);
    long long m2 = decrypt(c, keys.d, keys.n);
    assert(m == m2);
}

int test() {
    test_is_prime();
    test_gcd();
    test_mod_inv_basic();
    test_mod_inv_no_inverse();
    test_mod_inv_edge_cases();
    test_mod_inv_a_greater_than_b();
    test_mod_inv_large_values();
    test_mod_pow();
    test_encrypt_decrypt_small_numbers();
    test_encrypt_decrypt_edge_case();
    printf("All tests passed.\n");
    return 0;
}