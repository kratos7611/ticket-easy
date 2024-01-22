from django.db import models
from django.utils import timezone


class Event(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    address = models.TextField(blank=True, null=True)
    about = models.TextField(blank=False, null=False, default='')
    link = models.URLField(blank=True, null=True)
    thumbnail_image = models.ImageField(upload_to='event_thumbnails/')
    issued_ticket_quantity = models.PositiveIntegerField(default=1)
    booked_ticket_quantity = models.PositiveIntegerField(default=0, blank=True)
    price_per_ticket = models.DecimalField(max_digits=10, decimal_places=2)

    def available_ticket_quantity(self):
        return self.issued_ticket_quantity - self.booked_ticket_quantity

    def __str__(self):
        return self.title

    def day(self):
        return self.start_datetime.day

    def month(self):
        return self.start_datetime.strftime('%b')

    @property
    def status(self):
        now = timezone.localtime(timezone.now())
        if now < self.end_datetime and self.available_ticket_quantity() > 0 and self.issued_ticket_quantity > 0:
            return 'Active'
        else:
            return 'Deactivated'
