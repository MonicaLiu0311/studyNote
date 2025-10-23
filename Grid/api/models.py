from django.db import models
from django.utils import timezone

class ApiLog(models.Model):
    SUCCESS = 1
    FAILED = 0
    STATUS_CHOICES = (
        (SUCCESS, '成功'),
        (FAILED, '失败'),
    )
    
    caller = models.CharField(max_length=100, verbose_name='调用者')
    status = models.SmallIntegerField(choices=STATUS_CHOICES, verbose_name='状态')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    duration = models.FloatField(verbose_name='耗时(秒)')
    record_count = models.IntegerField(verbose_name='记录数量')
    error_message = models.TextField(null=True, blank=True, verbose_name='错误信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'api_log'
        verbose_name = 'API日志'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['caller', 'start_time']),
        ]