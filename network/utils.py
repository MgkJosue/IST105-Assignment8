import re
from datetime import datetime, timedelta

# Diccionario para mantener leases activos (en memoria)
active_leases = {}
ipv4_pool = set(range(10, 255))  # 192.168.1.10 - 192.168.1.254

def validate_mac_address(mac):
    """Valida formato de MAC address"""
    pattern = r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'
    return bool(re.match(pattern, mac))

def mac_to_bytes(mac):
    """Convierte MAC string a lista de bytes"""
    return [int(octet, 16) for octet in mac.split(':')]

def check_mac_sum_parity(mac_bytes):
    """Usa bitwise para verificar si la suma es par o impar"""
    total = sum(mac_bytes)
    # Bitwise AND con 1 para verificar si es impar
    is_odd = total & 1
    return "odd" if is_odd else "even"

def toggle_universal_bit(byte):
    """
    Toggle del 7mo bit (bit universal/local en EUI-64)
    Usa XOR bitwise con 0x02 (binario: 00000010)
    """
    return byte ^ 0x02

def generate_ipv4(mac):
    """Genera IPv4 desde pool para la MAC dada"""
    global active_leases, ipv4_pool
    
    # Verificar si ya tiene un lease activo
    if mac in active_leases:
        lease_info = active_leases[mac]
        if datetime.now() < lease_info['expiry']:
            return lease_info['ip']
        else:
            # Lease expiró, liberar IP
            if lease_info['ip'].startswith('192.168.1.'):
                last_octet = int(lease_info['ip'].split('.')[-1])
                ipv4_pool.add(last_octet)
    
    # Asignar nueva IP
    if not ipv4_pool:
        return None  # Pool agotado
    
    last_octet = ipv4_pool.pop()
    ip = f"192.168.1.{last_octet}"
    
    # Guardar lease
    expiry = datetime.now() + timedelta(seconds=3600)
    active_leases[mac] = {
        'ip': ip,
        'expiry': expiry,
        'type': 'DHCPv4'
    }
    
    return ip

def generate_ipv6_eui64(mac):
    """Genera IPv6 usando EUI-64 desde MAC"""
    mac_bytes = mac_to_bytes(mac)
    
    # Toggle del bit universal/local (7mo bit del primer byte)
    mac_bytes[0] = toggle_universal_bit(mac_bytes[0])
    
    # EUI-64: Insertar FF:FE en el medio
    # MAC: 00:1A:2B:3C:4D:5E
    # EUI-64: 00:1A:2B:FF:FE:3C:4D:5E
    eui64 = mac_bytes[:3] + [0xFF, 0xFE] + mac_bytes[3:]
    
    # Formar IPv6: 2001:db8::XXXX:XXFF:FEXX:XXXX
    ipv6_suffix = ':'.join([
        f"{eui64[0]:02x}{eui64[1]:02x}",
        f"{eui64[2]:02x}{eui64[3]:02x}",
        f"{eui64[4]:02x}{eui64[5]:02x}",
        f"{eui64[6]:02x}{eui64[7]:02x}"
    ])
    
    ipv6 = f"2001:db8::{ipv6_suffix}"
    
    # Guardar lease
    expiry = datetime.now() + timedelta(seconds=3600)
    active_leases[mac] = {
        'ip': ipv6,
        'expiry': expiry,
        'type': 'DHCPv6'
    }
    
    return ipv6