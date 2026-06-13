# VTP Attack - VLAN Trunking Protocol Spoofing
**Autor:** Yeury Lopez  
**Matrícula:** 2025-0780  
**Curso:** Networking Security  

---

## 📹 Video del Ataque
> [https://www.youtube.com/watch?v=bUu-CFBoF-Y]

---

## 🎯 Objetivo del Laboratorio

Demostrar cómo un atacante puede explotar el protocolo VTP (VLAN Trunking Protocol) para agregar y eliminar VLANs en toda la infraestructura de red, comprometiendo la segmentación de red sin necesidad de acceso físico a los switches.

---

## 🎯 Objetivo del Script

El script `vtp_attack.py` simula un servidor VTP malicioso que envía paquetes VTP falsificados con un número de revisión superior al del servidor legítimo, forzando a los switches del dominio a aceptar y propagar cambios no autorizados en la base de datos de VLANs.

### Parámetros usados

| Parámetro | Valor | Descripción |
|---|---|---|
| `IFACE` | `eth2` | Interfaz de red del atacante |
| `SRC_MAC` | Auto-detectada | MAC address de la interfaz |
| `DST_MAC` | `01:00:0c:cc:cc:cc` | Multicast Cisco VTP |
| `DOMAIN` | `LAB-YEURY` | Dominio VTP objetivo |
| `MD5_AGREGAR` | `\x70\x88...` | MD5 para agregar VLANs |
| `MD5_BORRAR` | `\xC6\x24...` | MD5 para borrar VLANs |
| `revision=999` | 999 | Revision number PASO 1 |
| `revision=1999` | 1999 | Revision number PASO 2 |

### Requisitos para utilizar la herramienta

```bash
# Sistema operativo
Kali Linux

# Dependencias
pip3 install scapy

# Permisos
sudo (root)

# Red
Puerto conectado en modo trunk al switch objetivo
Dominio VTP sin password configurado
```

---

## 📋 Documentación del funcionamiento del script

El script opera en dos pasos:

**PASO 1 — Agregar VLANs maliciosas:**
1. Construye un paquete VTP Summary Advertisement con revision 999
2. Incluye el MD5 correcto obtenido del debug del switch
3. Construye un paquete VTP Subset Advertisement con las VLANs existentes más las maliciosas (100 y 200)
4. Encapsula en frame 802.3 con SNAP header Cisco
5. Envía el Summary, espera 1 segundo, envía el Subset dos veces

**PASO 2 — Borrar VLANs:**
1. Mismo proceso con revision 1999
2. El Subset solo contiene las VLANs originales (sin 100 y 200)
3. El switch reemplaza su base de datos completa

```
Kali → [VTP Summary rev=999] → SW1 → acepta (rev > actual)
Kali → [VTP Subset con VLAN 100,200] → SW1 → propaga a SW2
SW1/SW2 → show vlan brief → VLANs 100 y 200 presentes ✅
```

> **Nota:** El MD5 debe obtenerse del debug del switch antes de ejecutar:
> ```
> SW1# debug sw-vlan vtp packets
> ```
> Buscar la línea: `MD5 digest failing calculated = XX XX XX...`

---

## 🌐 Documentación de la Red

### Topología
<img width="975" height="717" alt="image" src="https://github.com/user-attachments/assets/07c7fc43-b902-4c26-9c60-fe877b0ccb42" />


### VLANs

| VLAN ID | Nombre | Uso |
|---|---|---|
| 10 | ATACANTE | Red de Kali Linux |
| 20 | VICTIMA | Red de Tiny Core |
| 99 | MANAGEMENT | VLAN de gestión |
| 100 | VLAN-HACK-100 | VLAN maliciosa (creada por ataque) |
| 200 | VLAN-HACK-200 | VLAN maliciosa (creada por ataque) |

### Direccionamiento IP

| Dispositivo | Interfaz | IP | VLAN |
|---|---|---|---|
| Kali Linux | eth2 | 172.20.25.100/24 | 10 |
| Tiny Core | eth1 | 172.7.80.100/24 | 20 |
| Router | fa0/0.10 | 172.20.25.1/24 | 10 |
| Router | fa0/0.20 | 172.7.80.1/24 | 20 |

### Configuración VTP

| Parámetro | SW1 | SW2 |
|---|---|---|
| Modo | Server | Client |
| Dominio | LAB-YEURY | LAB-YEURY |
| Versión | 2 | 2 |
| Password | Ninguno | Ninguno |

---

## 📸 Capturas de pantalla requeridas



<img width="663" height="316" alt="image" src="https://github.com/user-attachments/assets/b42df550-6fa0-4bb9-a876-2b9ffe52728b" />

> — `show vtp status` en SW1 con revision 0

<img width="505" height="214" alt="image" src="https://github.com/user-attachments/assets/4de945b8-f111-4008-8ea4-d0fe8b810ac1" />

> — `show vlan brief` en SW1 antes del ataque

<img width="468" height="312" alt="image" src="https://github.com/user-attachments/assets/5227cff6-3d9f-4b5b-b75e-0c2ba6f7c609" />

> — Script corriendo en Kali (PASO 1)

<img width="647" height="186" alt="image" src="https://github.com/user-attachments/assets/213a39e7-80f2-4eeb-a918-c8f5f62e4936" />

> — `show vlan brief` en SW2 con VLANs 100 y 200

<img width="639" height="307" alt="image" src="https://github.com/user-attachments/assets/59c02fd9-7d49-4960-b250-b0de88da221d" />

> — `show vtp status` con revision 999

<img width="537" height="537" alt="image" src="https://github.com/user-attachments/assets/f9ec4ade-ee5b-40f0-8f4e-9c1c2b7aa783" />

> — Script corriendo PASO 2 (borrar)

<img width="550" height="214" alt="image" src="https://github.com/user-attachments/assets/d57ccecb-15d5-4df0-8162-c607552d83a9" />

> — `show vlan brief` sin VLANs 100 y 200

<img width="353" height="65" alt="image" src="https://github.com/user-attachments/assets/56c6c893-3531-449d-a50f-504b8a35b6e8" />

> — Configuración del password VTP en SW1

<img width="800" height="359" alt="image" src="https://github.com/user-attachments/assets/372fb3cc-36fd-4d48-92fc-e1e0defecd8f" />

> — Script ejecutándose con contramedida activa (no funciona)

---

## 🛡️ Contramedidas

### Contramedida 1 — Configurar VTP Password

```
SW1# configure terminal
SW1(config)# vtp password cisco123
SW1(config)# end

SW2# configure terminal
SW2(config)# vtp password cisco123
SW2(config)# end
```

**Por qué funciona:** El password VTP genera un MD5 que se incluye en cada paquete. Los switches validan este MD5 y rechazan cualquier actualización que no tenga el hash correcto.

### Contramedida 2 — Usar VTP Modo Transparent

```
SW1# configure terminal
SW1(config)# vtp mode transparent
SW1(config)# end
```

**Por qué funciona:** En modo transparent, el switch no acepta ni propaga actualizaciones VTP, ignorando completamente los paquetes maliciosos.

### Contramedida 3 — Deshabilitar VTP completamente

```
SW1# configure terminal
SW1(config)# vtp mode off
SW1(config)# end
```

**Por qué funciona:** VTP deshabilitado significa que el switch no procesa ningún paquete VTP entrante.

---

## 🔧 Cómo ejecutar

```bash
# 1. Clonar el repositorio
git clone https://github.com/[usuario]/vtp-attack

# 2. Instalar dependencias
pip3 install scapy

# 3. Obtener MD5 del switch (ver instrucciones en el script)
# SW1# debug sw-vlan vtp packets

# 4. Actualizar MD5 en el script
# Editar MD5_AGREGAR con el valor obtenido

# 5. Ejecutar
sudo python3 vtp_attack.py
```

---

## ⚠️ Disclaimer

Este script es únicamente para fines educativos y de laboratorio. El uso de esta herramienta en redes sin autorización expresa es ilegal y está penado por la ley.
