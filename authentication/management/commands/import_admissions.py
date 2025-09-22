import json
from django.core.management.base import BaseCommand
from authentication.models import AdmissionNumber

class Command(BaseCommand):
    help = "Import admission numbers from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to the JSON file")

    def handle(self, *args, **options):
        file_path = options["file"]

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for entry in data:
            obj, created = AdmissionNumber.objects.get_or_create(
                admission_number=entry["admission_number"],
                defaults={"full_name": entry.get("full_name", "")}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Added {obj.admission_number}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Skipped {obj.admission_number} (already exists)"))
