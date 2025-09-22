from django.contrib import admin
from .models import CustomUser, AdmissionNumber, otp,VotingID,AuditLog
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(AdmissionNumber)    
admin.site.register(otp)
admin.site.register(VotingID)
admin.site.register(AuditLog)