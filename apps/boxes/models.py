from django.db import models

class BoxCategory(models.Model):
    name = models.CharField("Tên loại box", max_length=50)

    class Meta:
        verbose_name = "Loại Box"
        verbose_name_plural = "Danh mục loại Box"

    def __str__(self):
        return self.name
    
class Box(models.Model):
    STATUS_CHOICES = (
        ('available', 'Đang trống'),
        ('pending', 'Chờ phê duyệt'),
        ('confirmed', 'Chờ Check-in'),
        ('active', 'Đang sử dụng'),
        ('completed', 'Đã hoàn thành'),
    )
    name = models.CharField("Tên Box", max_length=100)
    category = models.ForeignKey(BoxCategory, verbose_name="Loại Box", on_delete=models.SET_NULL, null=True, blank=True)
    capacity = models.IntegerField("Sức chứa")
    price_per_hour = models.DecimalField("Giá theo giờ", max_digits=10, decimal_places=2)
    status = models.CharField("Trạng thái", max_length=20, choices=STATUS_CHOICES, default='available')
    description = models.TextField("Mô tả", blank=True)
    image = models.ImageField("Hình ảnh", upload_to='boxes/', blank=True, null=True)

    class Meta:
        verbose_name = "Không gian Box"
        verbose_name_plural = "Danh sách các Box"

    def __str__(self):
        return f"{self.name} - Sức chứa (người): {self.capacity}"
