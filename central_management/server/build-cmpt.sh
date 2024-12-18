#!/bin/bash

source /morello/env/morello-sdk

clang  -march=morello --target=aarch64-linux-musl_purecap --sysroot=${MUSL_HOME} -DUSE_COMPARTMENTS  -g -c func.S
clang  -march=morello --target=aarch64-linux-musl_purecap --sysroot=${MUSL_HOME} -g -c comp.c
clang  -march=morello --target=aarch64-linux-musl_purecap --sysroot=${MUSL_HOME} -g  comp.o func.o -static -o payment_comp

clang  -march=morello --target=aarch64-linux-musl_purecap --sysroot=${MUSL_HOME} -g -c func.S
clang  -march=morello --target=aarch64-linux-musl_purecap --sysroot=${MUSL_HOME} -g -c comp.c
clang  -march=morello --target=aarch64-linux-musl_purecap --sysroot=${MUSL_HOME} -g  comp.o func.o -static -o payment_nocomp