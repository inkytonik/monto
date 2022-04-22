#ifndef BROKER_H
#define BROKER_H

#define ADDR_SIZE 50

struct config {
    char *from_sources_addr;
    char *to_servers_addr;
    char *from_servers_addr;
    char *to_sinks_addr;
    int threads;
};

void broker(struct config*);
int load_config(const char *config_file, struct config*);

#endif
