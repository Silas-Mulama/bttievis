from django.contrib import admin
from .models import Election,Candidate,Candidate_Position,Vote,spoiled_votes

# Register your models here.
admin.site.register(Election)
admin.site.register(Candidate)
admin.site.register(Candidate_Position)   
admin.site.register(Vote)
admin.site.register(spoiled_votes)

