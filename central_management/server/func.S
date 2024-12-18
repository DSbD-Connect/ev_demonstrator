.global run_func                ;
        .balign 16                      ;
        .type run_func, %function       ;
run_func:
        // Preserve original stack pointer
        mov c18, csp

        // Save return address and frame pointer
        adr c19, exit_compartment
        sub csp, csp, #160       // Increased stack allocation

        // Save important capability registers
        str c30, [csp, #144]     // Save Return address
        str c29, [csp, #128]     // Save Frame pointer
        str c19,  [csp, #112]     // Save Exit compartment address
        str c18,  [csp, #96]      // Save Original stack pointer

        // Store function pointer and arguments
        str c0,  [csp, #0]       // Function pointer
        str c1,  [csp, #16]      // First argument
        str c2,  [csp, #32]      // Second argument
        str c3,  [csp, #48]      // Third argument
        str c4,  [csp, #64]      // Fourth argument
        //str c5,  [csp, #80]      // Fifth argument

        // Set up signal handler

        //mov x10, x0
        //mov x11, x1

        //ldr x0, =2
        //ldr x1, =sigsegv_handler
        //bl signal                // Call the signal function

        //mov x0, x10
        //mov x1, x11

        // Prepare stack pointer
        mov c18, csp
        add c18, c18, #96
        seal c18, c18, lpb

#ifdef  USE_COMPARTMENTS
        //sub csp, csp, #65536
        sub csp,csp, #8, LSL #12 // Subtract 32768 (=2^15)
        sub csp,csp, #8, LSL #12 // Subtract 32768 (=2^15)
        mov x8, #32784 // = 32768 + 16
        add x8, x8, #32768
        //mov x8,#32784 // = 32768 + 16
        scbnds csp,csp,x8
        add csp,csp,#8, LSL #12 // Add 32768 (=2^15)
        add csp,csp,#8, LSL #12
        //add csp, csp, #65536

#endif
        ldr c17, [csp, #0]        // Load function pointer
        str c18, [csp] // Store modified stack pointer

        // Reload function pointer and arguments for function call

        //ldr c0, [csp, #16]       // Load First argument
        //ldr c1, [csp, #32]       // Load Second argument
        //ldr c2, [csp, #48]       // Load Third argument
        //ldr c3, [csp, #64]       // Load Fourth argument

        mov c0, c1
        mov c1, c2
        mov c2, c3
        mov c3, c4
        //mov c4, c5

        // Call the function
        blr c17

        // Restore and exit
        ldr c18, [csp]       // Restore original stack pointer
        ldpblr c29, [c18]         // Restore frame pointer and return address

        .global exit_compartment  ;
        .balign 16                ;
        .type exit_compartment, %function ;
exit_compartment:
        mov csp, c29             // Restore the stack pointer
        ldr c29, [csp, #-32]     // Restore frame pointer
        ldr c30, [csp, #-16]     // Restore return address
        ret
