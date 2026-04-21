import json
import os
from django.core.management.base import BaseCommand
from profiles.models import Profile
from django.conf import settings

class Command(BaseCommand):
    help = 'Seed database with profile data from JSON file'
    
    def handle(self, *args, **options):
        # Path to the JSON file in project root
        json_file_path = os.path.join(settings.BASE_DIR, 'seed_profiles.json')
        
        self.stdout.write(f"Looking for data file at: {json_file_path}")
        
        # Check if file exists
        if not os.path.exists(json_file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {json_file_path}"))
            self.stdout.write("Please place seed_profiles.json in the project root directory")
            return
        
        self.stdout.write("Loading profile data...")
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Invalid JSON file: {e}"))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to read file: {e}"))
            return
        
        # Handle both JSON structures: 
        # 1. Direct array: [{"name": "..."}, ...]
        # 2. Object with "profiles" key: {"profiles": [{"name": "..."}, ...]}
        if isinstance(data, dict) and 'profiles' in data:
            profiles_data = data['profiles']
            self.stdout.write(f"Found profiles array inside 'profiles' key")
        elif isinstance(data, list):
            profiles_data = data
            self.stdout.write(f"Found direct profiles array")
        else:
            self.stdout.write(self.style.ERROR(f"Unexpected JSON structure. Expected array or object with 'profiles' key."))
            return
        
        self.stdout.write(f"Found {len(profiles_data)} profiles in file")
        
        profiles_created = 0
        profiles_skipped = 0
        errors = 0
        
        for idx, item in enumerate(profiles_data):
            name = item.get('name', '').strip().lower()
            
            if not name:
                self.stdout.write(self.style.WARNING(f"Skipping item {idx}: No name field"))
                errors += 1
                continue
            
            # Check if profile already exists
            if Profile.objects.filter(name=name).exists():
                profiles_skipped += 1
                continue
            
            # Create profile
            try:
                Profile.objects.create(
                    name=name,
                    gender=item.get('gender'),
                    gender_probability=item.get('gender_probability'),
                    age=item.get('age'),
                    age_group=item.get('age_group'),
                    country_id=item.get('country_id'),
                    country_name=item.get('country_name'),
                    country_probability=item.get('country_probability'),
                )
                profiles_created += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating profile {name}: {e}"))
                errors += 1
            
            # Progress indicator
            if profiles_created % 100 == 0 and profiles_created > 0:
                self.stdout.write(f"  Created {profiles_created} profiles...")
        
        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Seeding complete!\n"
            f"   Created: {profiles_created}\n"
            f"   Skipped (duplicates): {profiles_skipped}\n"
            f"   Errors: {errors}\n"
            f"   Total in database: {Profile.objects.count()}"
        ))