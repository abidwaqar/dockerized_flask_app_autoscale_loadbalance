import psutil
import docker
import os
import time

HAPROXY_PORT = ":80"
INITIAL_SERVER_PORT = 5000
client = docker.from_env()
current_containers = 0
DEFAULT_SERVER_NAME = "cloud_web_app_"
container_dict = {}

HAPROXY_CONTENT =   "global\n\tlog /dev/log	local0\n\tlog /dev/log	local1 notice\n\tchroot /var/lib/haproxy\n\tstats " \
                    "socket /run/haproxy/admin.sock mode 660 level admin expose-fd listeners\n\tstats timeout 30s\n\tuser " \
                    "haproxy\n\tgroup haproxy\n\tdaemon\n\n\tca-base /etc/ssl/certs\n\tcrt-base " \
                    "/etc/ssl/private\n\n\tssl-default-bind-ciphers " \
                    "ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:RSA+AESGCM:RSA+AES:!aNULL:!MD5:!DSS\n" \
                    "\tssl-default-bind-options no-sslv3\n\ndefaults\n\tlog	" \
                    "global\n\tmode\thttp\n\toption\thttplog\n\toption\tdontlognull\n\t\ttimeout connect 5000\n\t\ttimeout " \
                    "client  50000\n\t\ttimeout server  50000\n\terrorfile 400 /etc/haproxy/errors/400.http\n\terrorfile " \
                    "403 /etc/haproxy/errors/403.http\n\terrorfile 408 /etc/haproxy/errors/408.http\n\terrorfile 500 " \
                    "/etc/haproxy/errors/500.http\n\terrorfile 502 /etc/haproxy/errors/502.http\n\terrorfile 503 " \
                    "/etc/haproxy/errors/503.http\n\terrorfile 504 /etc/haproxy/errors/504.http\n\nfrontend " \
                    "localnodes\n\tbind *:80\n\tmode http\n\tdefault_backend nodes\n\nbackend nodes\n\tmode " \
                    "http\n\tbalance roundrobin\n\toption forwardfor\n\thttp-request set-header X-Forwarded-Port %[" \
                    "dst_port]\n\thttp-request add-header X-Forwarded-Proto https if { ssl_fc }\n\toption httpchk HEAD / " \
                    "HTTP/1.1 "

# Writes the default setting to haproxy file
def initial_config_file_setup():
    config_file = open("/etc/haproxy/haproxy.cfg", "w+")
    config_file.write(HAPROXY_CONTENT)
    config_file.close()

# Restarts haproxy service
def restart_haproxy_service():
    os.system("sudo service haproxy restart")

# Creates container and adds name to haproxy 
def create_container_and_add_to_haproxy():
    container_name = DEFAULT_SERVER_NAME + str(current_containers)
    port = INITIAL_SERVER_PORT + current_containers
    container_dict[container_name] = client.containers.run("cloud_web_app:latest", detach=True, ports={'5000/tcp': port})
    config_file = open("/etc/haproxy/haproxy.cfg", "a+")
    config_file.write("\n\tserver " + container_name + " 127.0.0.1:" + str(port) + " check")
    config_file.close()

# Deleted container and its name from haproxy
def delete_container_and_remove_from_haproxy():
    container_name = DEFAULT_SERVER_NAME + str(current_containers - 1)
    port = INITIAL_SERVER_PORT + current_containers - 1

    # Deleting webserver line from haproxy config file
    with open("/etc/haproxy/haproxy.cfg", "r") as f:
        lines = f.readlines()
    with open("/etc/haproxy/haproxy.cfg", "w") as f:
        for line in lines:
            if line.strip("\n") != ("\tserver " + container_name + " 127.0.0.1:" + str(port) + " check"):
                f.write(line)

    container_dict[container_name].stop()
    container_dict[container_name].remove()

if __name__ == "__main__":
    initial_config_file_setup()

    while 1:
        try:
            haproxy_restart_flag = False
            cpu_usage = psutil.cpu_percent(interval=1)
            if cpu_usage < 10.0:
                N = 1
            else:
                N = int(cpu_usage/10.0)

            while (N - current_containers) != 0:
                haproxy_restart_flag = True
                if N > current_containers:
                    print ("Creating container")
                    create_container_and_add_to_haproxy()
                    current_containers += 1
                else:
                    print ("Removing container")
                    delete_container_and_remove_from_haproxy()
                    current_containers -= 1

            if (haproxy_restart_flag == True):
                restart_haproxy_service()
            time.sleep(15)
        except KeyboardInterrupt:
            break
    
    print ("Removing all containers")
    while (current_containers != 0):
        delete_container_and_remove_from_haproxy()
        current_containers -= 1

    print ("Program stopped")