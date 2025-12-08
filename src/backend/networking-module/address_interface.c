#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include "address_interface.h"

int resolve_host(char *hostname, struct sockaddr_in *ipv4, struct sockaddr_in6 *ipv6)
{
    struct addrinfo *resolved, *iterating_pointer;
    int counter = 0;
    int status;

    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    status = getaddrinfo(hostname, NULL, &hints, &resolved);

    if(status != 0)
    {
        return status;
    }

    ipv4 = NULL;
    ipv6 = NULL;
    
    for(iterating_pointer = resolved; iterating_pointer != NULL; iterating_pointer = iterating_pointer->ai_next)
    {
        if(iterating_pointer->ai_family == AF_INET)
        {
            ipv4 = (struct sockaddr_in *)iterating_pointer->ai_addr;
        } 
        else 
        {
            ipv6 = (struct sockaddr_in6 *)iterating_pointer->ai_addr;
        }
    }

    freeaddrinfo(resolved);
    return 0;
}

int main()
{
    memset(&hints, 0, sizeof hints);

    struct sockaddr_in *ipv4;
    struct sockaddr_in6 *ipv6;

    char ip_string[INET6_ADDRSTRLEN];

    int status = resolve_host("www.youtube.com", ipv4, ipv6);

    if(status != 0)
    {
        printf("Error: %s\n", gai_strerror(status));
        return 1;
    }

    inet_ntop(AF_INET, &(ipv4->sin_addr), ip_string, sizeof ip_string);
    printf("IPv4: %s\n", ip_string);

    inet_ntop(AF_INET6, &(ipv6->sin6_addr), ip_string, sizeof ip_string);
    printf("IPv6: %s\n\n", ip_string);
    
    return 0;
}