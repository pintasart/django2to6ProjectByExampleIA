from django.core.management.base import BaseCommand

from shop.models import Category, Product


class Command(BaseCommand):
    help = "Add missing English translations from first available language."

    def handle(self, *args, **options):
        category_updated = 0
        category_skipped = 0
        product_updated = 0
        product_skipped = 0

        for category in Category.objects.all():
            languages = list(category.get_available_languages())
            if "en" in languages:
                continue
            if not languages:
                category_skipped += 1
                continue

            source_lang = languages[0]
            source_translation = category.get_translation(source_lang)

            category.set_current_language("en")
            category.name = source_translation.name
            category.slug = source_translation.slug
            category.save()
            category_updated += 1

        for product in Product.objects.all():
            languages = list(product.get_available_languages())
            if "en" in languages:
                continue
            if not languages:
                product_skipped += 1
                continue

            source_lang = languages[0]
            source_translation = product.get_translation(source_lang)

            product.set_current_language("en")
            product.name = source_translation.name
            product.slug = source_translation.slug
            product.description = source_translation.description
            product.save()
            product_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Categories updated: {0} | Categories skipped(no translations): {1}".format(
                    category_updated, category_skipped
                )
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Products updated: {0} | Products skipped(no translations): {1}".format(
                    product_updated, product_skipped
                )
            )
        )
