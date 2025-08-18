from django.core.management.base import BaseCommand, CommandError
from community.utils.news_importer import import_news_from_json

class Command(BaseCommand):
    help = "Import Daum-cluster JSON file into NewsArticle/NewsSource."

    def add_arguments(self, parser):
        parser.add_argument("path", type=str, help="Path to JSON file")

    def handle(self, *args, **options):
        path = options["path"]
        try:
            count = import_news_from_json(path)
        except FileNotFoundError:
            raise CommandError(f"File not found: {path}")
        self.stdout.write(self.style.SUCCESS(f"Imported {count} article(s) from {path}"))
