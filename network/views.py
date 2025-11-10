from django.shortcuts import render
from django.conf import settings
from pymongo import MongoClient
from datetime import datetime
from .forms import DHCPRequestForm
from .utils import (
    validate_mac_address,
    mac_to_bytes,
    check_mac_sum_parity,
    generate_ipv4,
    generate_ipv6_eui64
)

# Conexión a MongoDB
def get_mongo_collection():
    config = settings.MONGODB_CONFIG
    client = MongoClient(config['host'], config['port'])
    db = client[config['database']]
    return db[config['collection']]

def dhcp_request(request):
    result = None
    error = None
    
    if request.method == 'POST':
        form = DHCPRequestForm(request.POST)
        
        if form.is_valid():
            mac = form.cleaned_data['mac_address'].upper()
            dhcp_version = form.cleaned_data['dhcp_version']
            
            # Validar MAC
            if not validate_mac_address(mac):
                error = "Invalid MAC address format"
            else:
                # Obtener bytes de MAC y calcular paridad
                mac_bytes = mac_to_bytes(mac)
                parity = check_mac_sum_parity(mac_bytes)
                
                # Generar IP según versión
                if dhcp_version == 'DHCPv4':
                    assigned_ip = generate_ipv4(mac)
                else:  # DHCPv6
                    assigned_ip = generate_ipv6_eui64(mac)
                
                if assigned_ip:
                    # Preparar documento para MongoDB
                    lease_doc = {
                        'mac_address': mac,
                        'dhcp_version': dhcp_version,
                        'assigned_ip': assigned_ip,
                        'lease_time': '3600 seconds',
                        'timestamp': datetime.utcnow().isoformat() + 'Z',
                        'mac_sum_parity': parity
                    }
                    
                    # Guardar en MongoDB
                    try:
                        collection = get_mongo_collection()
                        collection.insert_one(lease_doc)
                        
                        result = {
                            'mac_address': mac,
                            'assigned_ip': assigned_ip,
                            'dhcp_version': dhcp_version,
                            'lease_time': '3600 seconds',
                            'mac_sum_parity': parity
                        }
                    except Exception as e:
                        error = f"Database error: {str(e)}"
                else:
                    error = "No available IPs in pool"
    else:
        form = DHCPRequestForm()
    
    return render(request, 'network/dhcp_request.html', {
        'form': form,
        'result': result,
        'error': error
    })

def view_leases(request):
    try:
        collection = get_mongo_collection()
        leases = list(collection.find().sort('timestamp', -1))
        
        # Remover _id de MongoDB para display
        for lease in leases:
            lease.pop('_id', None)
            
    except Exception as e:
        leases = []
        error = str(e)
    
    return render(request, 'network/view_leases.html', {
        'leases': leases
    })