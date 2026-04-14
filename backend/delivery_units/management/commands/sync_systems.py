from django.core.management.base import BaseCommand
from delivery_units.models import System
from delivery_units.services.hac_api import get_all_rise_systems
import re

class Command(BaseCommand):
    help = 'Sync systems from HAC API'

    def handle(self, *args, **kwargs):
        self.stdout.write("Fetching systems from HAC...")
        systems_data = get_all_rise_systems()
        
        count_created = 0
        count_updated = 0

        for sys_data in systems_data:
            # We need to map the flat dict from get_all_rise_systems back to our model structure
            # Note: get_all_rise_systems already did some processing (splitting by tenant)
            
            # Extract virtual_hostname and domain from the combined Hostname
            hostname_parts = sys_data['Hostname'].split('.', 1)
            virtual_hostname = hostname_parts[0]
            domain = hostname_parts[1] if len(hostname_parts) > 1 else ""

            # Instance number is inside Port (43XX)
            instance_number = int(sys_data['Port'][2:]) if sys_data['Port'].startswith('43') else 0

            system, created = System.objects.update_or_create(
                name=sys_data['SID'],
                tenant=sys_data['Tenant'] if sys_data['Tenant'] != "N/A" else None,
                virtual_hostname=virtual_hostname,
                defaults={
                    'domain': domain,
                    'stage': sys_data['Stage'],
                    'instance_number': instance_number,
                    'is_rise': True,
                }
            )

            if created:
                count_created += 1
            else:
                count_updated += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully synced {len(systems_data)} systems (Created: {count_created}, Updated: {count_updated})"))
