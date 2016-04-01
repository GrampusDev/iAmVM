#!/usr/bin/python
"""
anti_vm_defense.py: Used to emulate virtual NAT so that all Anti VM techniques
that are based on virtual NAT behavior will return that the malware is running
inside virtual machine.
"""

from logging import getLogger, ERROR
getLogger("scapy.runtime").setLevel(ERROR)
from scapy.sendrecv import send
from scapy import route
from scapy.layers.inet import TCP, IP
from os import system
from netfilterqueue import NetfilterQueue
from random import randint
import socket


RST = 0x04
TCP_IP = '0.0.0.0'
TCP_PORT = 5009
BUFFER_SIZE = 1024

def get_new_ttl(curr_ttl):
    """
    If Windows TTL change to Linux and vice versa.

    :param curr_ttl: Current packet TTL.
    :return: int
    """
    return 64 if mode == 'Linux' else 128


def get_ip_id():
    """
    If Windows IP ID change to Linux and vice versa.

    :return: int
    """
    global id_counter
    if mode == 'Windows':
        id_counter += 1
        return id_counter - 1
    elif mode == 'Linux':
        return randint(2, 65535)


def handle_packet(pkt):
    """
    Apply packet handling logic.

    :param pkt: Received packet from network.
    """
    global id_counter
    scapy_packet = IP(pkt.get_payload())
    if IP in scapy_packet:
        scapy_packet[IP].ttl = get_new_ttl(scapy_packet[IP].ttl)
        # Change IP ID as Virtual NAT on Windows Host would do.
        scapy_packet[IP].id = get_ip_id()
        if TCP in scapy_packet and scapy_packet[TCP].flags & RST:
            scapy_packet[TCP].flags = 'FA'
        del scapy_packet[IP].chksum
        send(scapy_packet)
        print 'Drop Packet'
        pkt.drop()
    else:
        print 'Accept Packet'
        pkt.accept()


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)

    print 'Accepting connection on port ' + str(TCP_PORT)
    conn, addr = s.accept()
    try:
        print 'Connected client address:', addr
        mode = conn.recv(BUFFER_SIZE)
        if not mode:
            print 'No data received'
            conn.send("Error: No data received")
        else:
            print "Received mode:", mode
            conn.send("Network defence is up and running")
    finally:
        conn.close()
    system('iptables -A FORWARD -j NFQUEUE --queue-num 1')
    nfqueue = NetfilterQueue()
    nfqueue.bind(1, handle_packet)
    id_counter = 1000
    try:
        print 'Start changing packets as Virtual NAT with host OS ' + mode
        nfqueue.run()
    except KeyboardInterrupt:
        system('iptables -F')
        system('iptables -X')
        nfqueue.unbind()

