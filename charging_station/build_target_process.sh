source /morello/env/morello-sdk

clang -march=morello --target=aarch64-linux-musl_purecap --sysroot=${MUSL_HOME} simple_http_server.c -o simple_http_server_cheri  -static

# For cheri run the following process to be the target
# ./simple_http_server_cheri &

# For non cheri just run a simple python httpserver
# python -m http.server 5151 &
