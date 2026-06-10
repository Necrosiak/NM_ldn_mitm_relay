#pragma once
#include <stratosphere.hpp>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <cstring>
#include <unistd.h>
#include "debug.hpp"

namespace ams::mitm::ldn {

    class RelayClient {
        private:
            int fd = -1;
            struct sockaddr_in serverAddr = {};
            bool connected = false;
            char serverHost[128] = {};
            u16 serverPort = 11451;
            u32 lanIp = 0; // 10.13.x.x en network order

            static const u8 SLP_KEEPALIVE = 0;
            static const u8 SLP_IPV4      = 1;

        public:
            RelayClient() {}
            ~RelayClient() { disconnect(); }

            bool loadConfig() {
                // Valeurs par défaut
                strncpy(serverHost, "193.70.35.100", sizeof(serverHost));
                serverPort = 11451;
                lanIp = inet_addr("10.13.1.1");

                // Lire /atmosphere/config/ldn_mitm_relay.ini
                FILE *f = fopen("sdmc:/atmosphere/config/ldn_mitm_relay.ini", "r");
                if (!f) {
                    LogFormat("RelayClient: no config file, using defaults");
                    return true;
                }
                char line[256];
                while (fgets(line, sizeof(line), f)) {
                    char key[64], val[128];
                    if (sscanf(line, " %63[^=]= %127s", key, val) == 2) {
                        if (strcmp(key, "server") == 0) {
                            // format: host:port
                            char *colon = strrchr(val, ':');
                            if (colon) {
                                *colon = '\0';
                                strncpy(serverHost, val, sizeof(serverHost));
                                serverPort = (u16)atoi(colon + 1);
                            } else {
                                strncpy(serverHost, val, sizeof(serverHost));
                            }
                        } else if (strcmp(key, "ip") == 0) {
                            lanIp = inet_addr(val);
                        }
                    }
                }
                fclose(f);
                LogFormat("RelayClient: server=%s:%d ip=%s", serverHost, serverPort, inet_ntoa(*(struct in_addr*)&lanIp));
                return true;
            }

            bool connectRelay() {
                loadConfig();

                fd = ::socket(AF_INET, SOCK_DGRAM, 0);
                if (fd < 0) {
                    LogFormat("RelayClient: socket failed");
                    return false;
                }

                memset(&serverAddr, 0, sizeof(serverAddr));
                serverAddr.sin_family = AF_INET;
                serverAddr.sin_port = htons(serverPort);
                serverAddr.sin_addr.s_addr = inet_addr(serverHost);

                // Envoyer keepalive initial avec notre IP LAN
                sendKeepalive();

                connected = true;
                LogFormat("RelayClient: connected to %s:%d", serverHost, serverPort);
                return true;
            }

            void disconnect() {
                if (fd >= 0) {
                    ::close(fd);
                    fd = -1;
                }
                connected = false;
            }

            bool isConnected() const { return connected && fd >= 0; }
            int getFd() const { return fd; }
            u32 getLanIp() const { return lanIp; }

            // Envoie un paquet LAN brut vers le relay (encapsulé SLP)
            int sendLanPacket(const void *data, size_t size) {
                if (!isConnected()) return -1;

                // SLP: [1 byte type=1] [4 bytes src IP] [payload]
                size_t bufSize = 1 + 4 + size;
                u8 buf[bufSize];
                buf[0] = SLP_IPV4;
                memcpy(buf + 1, &lanIp, 4);
                memcpy(buf + 5, data, size);

                return ::sendto(fd, buf, bufSize, 0,
                    (struct sockaddr*)&serverAddr, sizeof(serverAddr));
            }

            // Reçoit un paquet du relay, retourne le payload LAN (sans header SLP)
            // retourne -1 si erreur, 0 si keepalive, >0 si paquet IPV4
            int recvLanPacket(void *outBuf, size_t bufSize, struct sockaddr_in *fromAddr) {
                if (!isConnected()) return -1;

                u8 buf[2048 + 5];
                socklen_t addrLen = sizeof(*fromAddr);
                ssize_t len = ::recvfrom(fd, buf, sizeof(buf), MSG_DONTWAIT,
                    (struct sockaddr*)fromAddr, &addrLen);

                if (len < 1) return (int)len;

                u8 type = buf[0];
                if (type == SLP_KEEPALIVE) return 0;
                if (type == SLP_IPV4 && len > 5) {
                    size_t payloadSize = len - 5;
                    if (payloadSize > bufSize) payloadSize = bufSize;
                    memcpy(outBuf, buf + 5, payloadSize);
                    return (int)payloadSize;
                }
                return 0;
            }

            void sendKeepalive() {
                if (fd < 0) return;
                u8 buf[5];
                buf[0] = SLP_KEEPALIVE;
                memcpy(buf + 1, &lanIp, 4);
                ::sendto(fd, buf, sizeof(buf), 0,
                    (struct sockaddr*)&serverAddr, sizeof(serverAddr));
            }
    };

} // namespace ams::mitm::ldn


