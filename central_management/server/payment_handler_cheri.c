#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <cheriintrin.h>
// Global seal key and sealed token
/*
static void *seal_key = 0x1234;
static void *sealed_token = NULL;
*/

typedef struct {
    void* sealed_cap;
    void* seal_key;
} sealed_token_t;


// Placeholder for retrieving a token from a Secure Enclave or TEE
char* secure_get_token() {
    // In a real-world use case, you would interact with the Secure Enclave API
    // to retrieve the token securely.
    
    // For the sake of this example, we simulate it with a hardcoded value:
    static char token[256];
    
    strcpy(token, "sk_live_secrettoken12345");
    return token;
}


void* get_seal_key() {
    // Generates a unique seal key
    return 0x1234;
}
/*
void* get_seal_key(unsigned long type) {
    void* seal_key;
    asm volatile(
        "mov x0, %1\n\t"
        "mrs %0, csealkey_el0\n\t"
        : "=r"(seal_key)
        : "r"(type)
    );
    return seal_key;
}
*/

void* seal_capability(void* cap, void* seal_key) {
    void* sealed_cap;
    asm volatile(
        "seal %0, %1, %2\n\t"
        : "=C"(sealed_cap)
        : "C"(cap), "C"(seal_key)
    );
    return sealed_cap;
}

void* unseal_capability(void* sealed_cap, void* seal_key) {
    void* unsealed_cap;
    asm volatile(
        "unseal %0, %1, %2\n\t"
        : "=C"(unsealed_cap)
        : "C"(sealed_cap), "C"(seal_key)
    );
    return unsealed_cap;
}


sealed_token_t create_sealed_token(void) {
    sealed_token_t result;

    // Define a unique type for this token
    unsigned long token_type = 0x42;

    // Get a seal key for this type
    result.seal_key = get_seal_key();

    // Seal the token capability
    result.sealed_cap = seal_capability(secure_get_token(), result.seal_key);

    return result;
}


void process_payment_cheri(const char* credit_card_number, const char* expiry_date, const char* cvv, const char* amount) {
    // Create and seal token
    sealed_token_t sealed_token = create_sealed_token();

    // Unseal token for secure use
    char* token = (char*)unseal_capability(sealed_token.sealed_cap, sealed_token.seal_key);

    // Use the token within bounds in a simulated payment
    printf("Processing payment securely...\n");
    printf("Credit Card: %s\n", credit_card_number);
    printf("Expiry Date: %s\n", expiry_date);
    printf("CVV: %s\n", cvv);
    printf("Amount: %s\n", amount);
    printf("Token (secured): %s\n", token);
}

/*
// Initialize token
void initialize_sealed_token() {
    if (sealed_token != NULL) {
        // Token is already initialized
        return;
    }

    
    
    // Generate a sealing key
    asm volatile("csealkey %0" : "=C"(seal_key));

    // Seal the token
    asm volatile(
        "cseal %0, %1, %2\n"
        : "=C"(sealed_token)
        : "C"(token), "C"(seal_key)
    );

    printf("Token initialized and sealed.\n");

    // Erase the token from memory
    //memset(env_token, 0, strlen(env_token));

    // Remove the environment variable to prevent later access
    //unsetenv("PAYMENT_TOKEN");
}
*/
/*
// Unseal and use the token for a payment request
void make_payment(const char *amount, const char *currency) {
    char *token;

    // Ensure the token has been initialized
    if (sealed_token == NULL) {
        fprintf(stderr, "Token not initialized. Call initialize_sealed_token() first.\n");
        exit(EXIT_FAILURE);
    }

    // Unseal the token
    asm volatile(
        "cunseal %0, %1, %2\n"
        : "=C"(token)
        : "C"(sealed_token), "C"(seal_key)
    );

    // Use CURL to make a payment request
    CURL *curl = curl_easy_init();
    if (curl) {
        struct curl_slist *headers = NULL;
        char auth_header[256];
        snprintf(auth_header, sizeof(auth_header), "Authorization: Bearer %s", token);

        headers = curl_slist_append(headers, auth_header);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_URL, "http://localhost:8000/charge");

        // Prepare the POST data
        char post_data[256];
        snprintf(post_data, sizeof(post_data), "amount=%s&currency=%s", amount, currency);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, post_data);

        CURLcode res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        }

        curl_easy_cleanup(curl);
    }
}
*/
int main(int argc, char *argv[]) {
    if (argc < 5) {
        fprintf(stderr, "Usage: %s <credit_card_number> <expiry_date> <cvv> <amount>\n", argv[0]);
        return 1;
    }

    const char* card_number = argv[1];
    const char* expiry_date = argv[2];
    const char* cvv = argv[3];
    const char* amount = argv[4];

    process_payment_cheri(card_number, expiry_date, cvv, amount);
    
    //initialize_sealed_token(); 
    //make_payment(credit_card_number, expiry_date, cvv, amount);

    return EXIT_SUCCESS;
}
