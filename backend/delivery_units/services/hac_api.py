import json
import requests
import re
from .config import HAC_API_URL, HAC_USER, HAC_PASS

def get_all_rise_systems():
    domain_filter = "rise\.sap\.schwarz"
    # Note: HAC_API_URL already ends with / if defined in .env
    params = {
        'domain__iregex': domain_filter,
        'page_size': 1000
    }
    
    try:
        # Using requests is much cleaner for Windows/Linux cross-platform
        response = requests.get(
            HAC_API_URL, 
            params=params, 
            auth=(HAC_USER, HAC_PASS),
            verify=False # Matches the -k flag in curl
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        
        rise_list = []
        for item in results:
            sid = item.get("name", "N/A")
            v_host = item.get("virtual_hostname", "N/A")
            domain = item.get("domain", "N/A")
            inst_num = item.get("instance_number")
            stage = item.get("stage", "N/A")
            connected_apps = item.get("connected_applications", "")
            
            alm_port = f"43{str(inst_num).zfill(2)}" if inst_num is not None else "N/A"
            tenants = re.findall(r'ABAP:([A-Za-z0-9]+)', connected_apps) if connected_apps else []

            if tenants and v_host != "N/A":
                for tenant in tenants:
                    new_v_host = v_host.lower().replace(sid.lower(), tenant.lower())
                    rise_list.append({
                        "SID": sid, "Tenant": tenant, "Hostname": f"{new_v_host}.{domain}", 
                        "Port": alm_port, "Stage": stage
                    })
            else:
                rise_list.append({
                    "SID": sid, "Tenant": "N/A", "Hostname": f"{v_host}.{domain}" if v_host != "N/A" else "N/A", 
                    "Port": alm_port, "Stage": stage
                })
        return rise_list
    except Exception as e:
        print(f"Error fetching systems: {e}")
        return []
