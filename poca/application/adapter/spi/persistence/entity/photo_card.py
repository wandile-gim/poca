from django.db import models

from poca.application.adapter.spi.persistence.entity.user import User
from poca.application.domain.model.photo_card import PhotoCard as PhotoCardDomain, PhotoCardState
from poca.application.domain.model.photo_card import PhotoCardSale as PhotoCardSaleDomain


class PhotoCard(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.CharField(max_length=255, blank=True, null=True)
    release_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'photo_cards'

    def to_domain(self):
        return PhotoCardDomain(
            id=self.id,
            name=self.name,
            description=self.description,
            image_url=self.image_url,
            release_date=str(self.release_date)
        )


class PhotoCardSale(models.Model):
    STATE_CHOICES = {
        ('판매중', 'On Sale'),
        ('판매완료', 'Sold Out')
    }

    photo_card = models.ForeignKey(PhotoCard, on_delete=models.CASCADE)
    state = models.CharField(max_length=10, choices=STATE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    fee = models.DecimalField(max_digits=10, decimal_places=0)
    buyer = models.ForeignKey(User, related_name='purchases', on_delete=models.SET_NULL, null=True, blank=True)
    seller = models.ForeignKey(User, related_name='sales', on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    renewal_date = models.DateTimeField(blank=True, null=True)
    sold_date = models.DateTimeField(null=True, blank=True)
    version = models.IntegerField(default=0)

    class Meta:
        db_table = 'photo_card_sales'

        # 자주 조회되는 조건이므로 인덱스를 추가
        indexes = [
            models.Index(fields=['photo_card', 'price', 'renewal_date']),
        ]

    def to_domain(self):
        return PhotoCardSaleDomain(
            id=self.id,
            photo_card=self.photo_card.to_domain(),
            state=PhotoCardState(self.state),
            price=self.price,
            fee=self.fee,
            seller=self.seller.to_domain(),
            buyer=self.buyer.to_domain() if self.buyer else None,
            create_date=str(self.create_date),
            renewal_date=str(self.renewal_date),
            sold_date=str(self.sold_date)
        )
