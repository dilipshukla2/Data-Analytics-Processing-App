# processor/management/commands/seed_mega_data.py
import random
import string
import time
from django.core.management.base import BaseCommand
from processor.models import Merchant, Customer, Product, Transaction

class Command(BaseCommand):
    help = 'Seeds complex relational data for maximum EC2 memory/CPU load'

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating master data...")
        merchants = [Merchant.objects.create(name=f"Merch_{i}", risk_tier=random.choice(['standard', 'high', 'critical'])) for i in range(500)]
        customers = [Customer.objects.create(email_hash=self._random_hash(), account_age_days=random.randint(1, 3650)) for _ in range(5000)]
        products = [Product.objects.create(sku=f"SKU_{i}", category=random.choice(['Electronics', 'Fashion', 'Crypto', 'GiftCards'])) for i in range(2000)]

        total_records = 10000000
        batch_size = 20000
        
        self.stdout.write(f"Starting insertion of {total_records} records. This will take 15-25 mins...")
        start_time = time.time()

        for i in range(0, total_records, batch_size):
            batch = []
            for _ in range(batch_size):
                # Randomly flag 10% as 'flagged' to make filtering interesting
                status = 'flagged' if random.random() < 0.1 else 'completed'
                batch.append(Transaction(
                    merchant=random.choice(merchants),
                    customer=random.choice(customers),
                    product=random.choice(products),
                    amount=random.uniform(10.0, 10000.0),
                    status=status
                ))
            
            Transaction.objects.bulk_create(batch, ignore_conflicts=True)
            
            if (i + batch_size) % 1000000 == 0:
                self.stdout.write(f"   -> Inserted {i + batch_size:,} records. Time: {time.time() - start_time:.2f}s")

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded 10 Million relational records!"))

    def _random_hash(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))