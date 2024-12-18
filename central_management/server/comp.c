#include <stdio.h>
#include <stdlib.h>
#include <cheriintrin.h>
#include <string.h>
#include <signal.h>
#include <setjmp.h>
#include <stdbool.h>

void run_func(void * func_ptr, const char* credit_card_number, const char* expiry_date, const char* cvv, const char* amount);
jmp_buf buf;
bool handler_enabled = true;
void sigsegv_handler(int signum);


void sigsegv_handler(int signum) {
  if (handler_enabled) {
    printf("Segmentation fault occurred. Debugging.\n");
    handler_enabled = false;
    longjmp(buf, 1); // Jump back to the last setjmp location
  } else {
        // Revert to the default behavior for SIGSEGV
  }
}

void func(const char* credit_card_number, const char* expiry_date, const char* cvv, const char* amount){
  void  *ptr;
  char *ch_ptr;
  int i;

  int offset;
  const int TOTAL_NUMBERS = 2000;
  char * card_providers[TOTAL_NUMBERS];

  // Fill the card_providers array
  for (int i = 0; i < TOTAL_NUMBERS; i++) {
       card_providers[i] = "Visa";
  }

  char* card_token = strtok(credit_card_number, "-");
  offset = atoi(card_token);

  if (setjmp(buf) == 0) {
    signal(SIGSEGV, sigsegv_handler);
    char **card_ptr = card_providers;
    printf("Card Provider %d: %s\n", offset, *(card_ptr + offset));

  }else{
    // Left out debug code by the developers
    // Exemplifies an information disclosure vulnerability
    asm("mov %0,csp":"=r" (ptr));
    ch_ptr = (char*)ptr;
    for(i=32500;i<(32768 + 2000);i++)
        printf("%c", ch_ptr[i]);
    printf("\n");
  }
}


int main(int argc, char *argv[]){
  char buff[100] = {'S','e','c','r','e','t',0};
  if (argc < 5) {
      fprintf(stderr, "Usage: %s <credit_card_number> <expiry_date> <cvv> <amount>\n", argv[0]);
      return 1;
  }

  const char* credit_card_number = argv[1];
  const char* expiry_date = argv[2];
  const char* cvv = argv[3];
  const char* amount = argv[4];

  run_func(func, credit_card_number,
                expiry_date,
                cvv,
                amount);

  return 0;
}