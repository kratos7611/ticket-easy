from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=255)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    address = models.TextField()
    link = models.URLField(blank=True, null=True)
    thumbnail_image = models.ImageField(upload_to='event_thumbnails/')
    issued_ticket_quantity = models.PositiveIntegerField()
    booked_ticket_quantity = models.PositiveIntegerField(default=0)
    price_per_ticket = models.DecimalField(max_digits=10, decimal_places=2)

    def available_ticket_quantity(self):
        return self.issued_ticket_quantity - self.booked_ticket_quantity

    def __str__(self):
        return self.title
