from django.core.management.base import BaseCommand
from listings.models import Listing
from django.contrib.auth.models import User
import random

class Command(BaseCommand):
    help = 'Seed the database with sample listings data'

    def handle(self, *args, **kwargs):
        # Create a default user to assign as owner
        user, created = User.objects.get_or_create(username='owner', defaults={'email': 'owner@example.com'})
        if created:
            user.set_password('password123')
            user.save()

        sample_listings = [
            {
                "title": "Cozy Cottage",
                "description": "A small cozy cottage in the countryside.",
                "price_per_night": 100,
                "location": "Countryside",
            },
            {
                "title": "Modern Apartment",
                "description": "A sleek apartment in the city center.",
                "price_per_night": 150,
                "location": "City Center",
            },
            {
                "title": "Beach House",
                "description": "A beautiful house with sea view.",
                "price_per_night": 200,
                "location": "Beachfront",
            },
        ]

        for listing_data in sample_listings:
            listing, created = Listing.objects.get_or_create(
                title=listing_data["title"],
                defaults={
                    'description': listing_data['description'],
                    'price_per_night': listing_data['price_per_night'],
                    'location': listing_data['location'],
                    'owner': user
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created listing: {listing.title}'))
            else:
                self.stdout.write(f'Listing already exists: {listing.title}')

        self.stdout.write(self.style.SUCCESS('Seeding complete!'))
