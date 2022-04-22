#include <stdio.h>
#include <signal.h>
#include <string.h>
#include <json-c/json.h>
#include <zmq.h>
#include "broker.h"

static int running = 1;

void stop(int sig) {
    running = 0;
}

void report_error(int err, const char *err_source);

void broker(struct config *conf)
{
    void *ctx = 0, *from_sources = 0, *to_servers = 0, *from_servers = 0, *to_sinks = 0;
    int err = 0; const char *err_source = 0; int size = 0;
    const int poll_timeout = 500;

    ctx          = zmq_ctx_new();
    from_sources = zmq_socket(ctx, ZMQ_REP);
    to_servers   = zmq_socket(ctx, ZMQ_PUB);
    from_servers = zmq_socket(ctx, ZMQ_REP);
    to_sinks     = zmq_socket(ctx, ZMQ_PUB);

    #define BIND(socket,addr) \
        do { \
            err = zmq_bind(socket, addr); \
            err_source = addr; \
            if(err != 0) goto FAIL; \
        } while(0)

    BIND(from_sources, conf->from_sources_addr);
    BIND(to_servers, conf->to_servers_addr);
    BIND(from_servers, conf->from_servers_addr);
    BIND(to_sinks, conf->to_sinks_addr);

    #undef BIND

    printf("listening on %s for requests from sources\n", conf->from_sources_addr);
    printf("responding on %s to servers\n", conf->to_servers_addr);
    printf("listening on %s for responses from servers\n", conf->from_servers_addr);
    printf("responding on %s to sinks\n", conf->to_sinks_addr);

    // Trap Ctrl-C to shutdown gracefully
    signal(SIGINT, stop);

    zmq_pollitem_t poller [] = {
        { from_sources, 0, ZMQ_POLLIN, 0},
        { from_servers, 0, ZMQ_POLLIN, 0}
    };

    zmq_msg_t msg;
    zmq_msg_init(&msg);

    while(running) {
        zmq_poll(poller, 2, poll_timeout);

        // from_sources has events ready
        if(poller[0].revents & ZMQ_POLLIN) {
            size = zmq_recvmsg(from_sources, &msg, 0);
            if(size != 0) {
                zmq_send_const(from_sources, "ack", 3, 0);
                zmq_sendmsg(to_servers, &msg, 0);
            }
        }

        // from_servers has events ready
        if(poller[1].revents & ZMQ_POLLIN) {
            size = zmq_recvmsg(from_servers, &msg, 0);
            if(size != 0) {
                zmq_send_const(from_servers, "ack", 3, 0);
                zmq_sendmsg(to_sinks, &msg, 0);
            }
        }
    }

    printf("Monto is shutting down\n");

    goto CLEANUP;

FAIL:
    report_error(err,err_source);

CLEANUP:
    zmq_msg_close(&msg);
    zmq_close(from_sources);
    zmq_close(to_servers);
    zmq_close(from_servers);
    zmq_close(to_sinks);
    zmq_term(ctx);

}

void report_error(int err, const char *err_source)
{
    switch (err) {
        case EINVAL:
             fprintf(stderr, "Invalid endpoint: %s", err_source);
             break;
        case EPROTONOSUPPORT:
             fprintf(stderr, "Invalid protocol: %s", err_source);
             break;
        case ENOCOMPATPROTO:
             fprintf(stderr, "Transport protocol incompatible with socket type: %s", err_source);
             break;
        case EADDRINUSE:
             fprintf(stderr, "Address is already in use: %s", err_source);
             break;
        case EADDRNOTAVAIL:
             fprintf(stderr, "Requested address is not local: %s", err_source);
             break;
        case ENODEV:
             fprintf(stderr, "Address specifies a nonexistent interface: %s", err_source);
             break;
        case ETERM:
             fprintf(stderr, "ZMQ context allready terminated: %s", err_source);
             break;
        case ENOTSOCK:
             fprintf(stderr, "The provided socket is invalid: %s", err_source);
             break;
        case EMTHREAD:
             fprintf(stderr, "No I/O thread is available to accomplish the task: %s", err_source);
             break;
    }
}

int load_config(const char *config_file, struct config* conf) {
	FILE *fd; int ret = 0;

	if((fd = fopen(config_file, "r")) == 0) {
		fprintf(stderr, "cannot read monto configuration file: %s", config_file);
		return -1;
	}
	
	// find out file size
	fseek(fd, 0L, SEEK_END);
	size_t file_size = ftell(fd);
	rewind(fd);

	char *buffer = (char*) malloc((file_size + 1) * sizeof(char));
	if(fread(buffer, sizeof(char), file_size, fd) != file_size) {
		fprintf(stderr, "monto configuration file changed during reading\n");
		ret = -1;
		goto FILE_CLEANUP;
	}

	json_tokener *tokener = json_tokener_new();
	json_object *config_json = json_tokener_parse_ex(tokener, buffer, file_size);

	enum json_tokener_error err;
	if((err = json_tokener_get_error(tokener)) != json_tokener_success) {
		fprintf(stderr, "error during json parsing of monto configuration: %s\n", json_tokener_error_desc(err));
		ret = -1;
		goto JSON_CLEANUP;
	}

	json_object *connection = 0;
	if(json_object_object_get_ex(config_json, "connections", &connection) == 0)
		goto JSON_CLEANUP;

	json_object *addr = 0;

    #define PARSE_KEY(key,to) \
		do { \
			addr = 0; \
			if(json_object_object_get_ex(connection, key, &addr) != 0) \
				strncpy(to, json_object_get_string(addr),ADDR_SIZE-1); \
		} while(0)

	PARSE_KEY("from_sources", conf->from_sources_addr);
	PARSE_KEY("to_servers",   conf->to_servers_addr);
	PARSE_KEY("from_servers", conf->from_servers_addr);
	PARSE_KEY("to_sinks",     conf->to_sinks_addr);

    #undef PARSE_KEY

JSON_CLEANUP:
	json_tokener_free(tokener);
	json_object_put(config_json);

FILE_CLEANUP:
	fclose(fd);
	free(buffer);
	return ret;
}

void new_config(struct config *conf)
{
	conf->from_sources_addr = malloc(ADDR_SIZE * sizeof(char));
	conf->to_servers_addr   = malloc(ADDR_SIZE * sizeof(char));
	conf->from_servers_addr = malloc(ADDR_SIZE * sizeof(char));
	conf->to_sinks_addr     = malloc(ADDR_SIZE * sizeof(char));

	// Set default values if the configuration file doesn't specify them.
	strncpy(conf->from_sources_addr, "tcp://127.0.0.1:5000", ADDR_SIZE-1);
	strncpy(conf->to_servers_addr,   "tcp://127.0.0.1:5001", ADDR_SIZE-1);
	strncpy(conf->from_servers_addr, "tcp://127.0.0.1:5002", ADDR_SIZE-1);
	strncpy(conf->to_sinks_addr,     "tcp://127.0.0.1:5003", ADDR_SIZE-1);
	conf->threads = 1;
}

void free_config(struct config *conf)
{
	free(conf->from_sources_addr);
	free(conf->to_servers_addr);
	free(conf->from_servers_addr);
	free(conf->to_sinks_addr);
}

int main() {
    struct config conf;
	new_config(&conf);

	char *HOME = getenv("HOME");

	char config_file[80];
	memset(config_file, '\0', 80);
	strncat(config_file,HOME,80);
	strncat(config_file,"/.monto",80);

	if(load_config(config_file, &conf) < 0) {
		fprintf(stderr, "Error during parsing of configuration file, aborting\n");
		free_config(&conf);
		return -1;
	}

    broker(&conf);
	free_config(&conf);
}
