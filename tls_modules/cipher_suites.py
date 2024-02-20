from Crypto.Cipher import AES

CipherSuites = {
    0xc02f: {
        "name": "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
        "mode": AES.MODE_GCM,
        "key_size": 16,
        "mac_size": 16,
        "iv_size": 12},

    0xcca9: {
        "name": "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
        "mode": "ChaCha20-Poly1305",
        "key_size": 32,
        "mac_size": 16,
        "iv_size": 12},

    0xcca8: {
        "name": "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
        "mode": "ChaCha20-Poly1305",
        "key_size": 32,
        "mac_size": 16,
        "iv_size": 12},

    0xc024: {
        "name": "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256",
        "mode": AES.MODE_CBC,
        "key_size": 16,
        "mac_size": 32,
        "iv_size": 16},

    0xc028: {
        "name": "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384",
        "mode": AES.MODE_CBC,
        "key_size": 32,
        "mac_size": 48,
        "iv_size": 16},

    0x009e: {
        "name": "TLS_DHE_RSA_WITH_AES_128_GCM_SHA256",
        "mode": AES.MODE_GCM,
        "key_size": 16,
        "mac_size": 16,
        "iv_size": 12},

    0x0067: {
        "name": "TLS_DHE_RSA_WITH_AES_128_CBC_SHA256",
        "mode": AES.MODE_CBC,
        "key_size": 16,
        "mac_size": 32,
        "iv_size": 16},

    0xc014: {
        "name": "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA",
        "mode": AES.MODE_CBC,
        "key_size": 32,
        "mac_size": 20,
        "iv_size": 16},

    0x0039: {
        "name": "TLS_DHE_RSA_WITH_AES_256_CBC_SHA",
        "mode": AES.MODE_CBC,
        "key_size": 32,
        "mac_size": 20,
        "iv_size": 16},

    0xc009: {
        "name": "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA",
        "mode": AES.MODE_CBC,
        "key_size": 16,
        "mac_size": 20,
        "iv_size": 16},

    0xc013: {
        "name": "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA",
        "mode": AES.MODE_CBC,
        "key_size": 16,
        "mac_size": 20,
        "iv_size": 16},

    0xc01f: {
        "name": "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256",
        "mode": AES.MODE_CBC,
        "key_size": 16,
        "mac_size": 32,
        "iv_size": 16},

    0x006b: {
        "name": "TLS_DHE_RSA_WITH_AES_256_CBC_SHA256",
        "mode": AES.MODE_CBC,
        "key_size": 32,
        "mac_size": 32,
        "iv_size": 16},

    0xc00a: {
        "name": "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA",
        "mode": AES.MODE_CBC,
        "key_size": 32,
        "mac_size": 20,
        "iv_size": 16},

    0x0033: {
        "name": "TLS_DHE_RSA_WITH_AES_128_CBC_SHA",
        "mode": AES.MODE_CBC,
        "key_size": 16,
        "mac_size": 20,
        "iv_size": 16},

    0x009c: {
        "name": "TLS_RSA_WITH_AES_128_GCM_SHA256",
        "mode": AES.MODE_GCM,
        "key_size": 16,
        "mac_size": 16,
        "iv_size": 12},

    0x009d: {
        "name": "TLS_RSA_WITH_AES_256_GCM_SHA384",
        "mode": AES.MODE_GCM,
        "key_size": 32,
        "mac_size": 16,
        "iv_size": 12},

    0xc00f: {
        "name": "TLS_RSA_WITH_AES_128_CBC_SHA256",
        "mode": AES.MODE_CBC,
        "key_size": 16,
        "mac_size": 32,
        "iv_size": 16},

    0xc005: {
        "name": "TLS_RSA_WITH_AES_256_CBC_SHA256",
        "mode": AES.MODE_CBC,
        "key_size": 32,
        "mac_size": 32,
        "iv_size": 16},

    0x0035: {
        "name": "TLS_RSA_WITH_AES_256_CBC_SHA",
        "mode": AES.MODE_CBC,
        "key_size": 32,
        "mac_size": 20,
        "iv_size": 16}
}