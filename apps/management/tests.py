from django.test import TestCase

# Create your tests here.

from datetime import datetime


from decimal import Decimal

print((Decimal(10.2) - Decimal(9.1)).quantize(Decimal('0.00')))