from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from uuid import uuid4
def default_end_datetime():
    return timezone.now() + timedelta(hours=8)

def TimeStampedModel():
    return timezone.now()


class Candidate_Position(models.Model):
    election = models.ForeignKey('Election', on_delete=models.CASCADE, related_name='positions')
    name = models.CharField(max_length=100)  # e.g. President, Secretary
    description = models.TextField(blank=True, null=True)
    added_on = models.DateTimeField(default=TimeStampedModel)
    
    class Meta:
        unique_together = ('election', 'name')  # Position names unique within an election\
        ordering = ['added_on']
    def __str__(self):
        return self.name
    
class Election(models.Model):
    name = models.CharField(max_length=200)
    id= models.UUIDField(primary_key=True, default=uuid4, editable=False)
    description = models.TextField(blank=True, null=True)
    
    # Use datetime instead of splitting date + time
    start_datetime = models.DateTimeField(default=timezone.now)
    end_datetime = models.DateTimeField(default=default_end_datetime)
    is_available  = models.BooleanField(default=True)  # If election is visible to users
      
    class Meta:
        ordering = ['start_datetime']

    def __str__(self):
        return self.name

    def is_active(self):
        """Check if the election is currently running"""
        now = timezone.now()
        return self.start_datetime <= now <= self.end_datetime

    def total_votes(self):
        """Count total votes cast in this election"""
        return self.votes.count()


class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=200)
    admission_number = models.CharField(max_length=50)
    party = models.CharField(max_length=100)
    position = models.ForeignKey(Candidate_Position, on_delete=models.CASCADE, related_name='candidates')
    image = models.ImageField(upload_to='candidates/', blank=True, null=True)
    manifesto = models.TextField(blank=True, null=True)
  

    class Meta:
        unique_together = ('election', 'name')  

    def __str__(self):
        return f"{self.name} ({self.party})"

    @property
    def total_votes(self):
        """Count how many votes this candidate received"""
        return self.votes.count()



class Vote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='votes')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    position = models.ForeignKey(Candidate_Position, on_delete=models.CASCADE)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voter', 'position')  # Prevent double voting
        ordering = ['-timestamp']

    def __str__(self):
        return f"Vote for {self.candidate.name} in {self.election.name} by {self.voter}"

    def clean(self):
        """Ensure the candidate belongs to the election before saving"""
        if self.candidate.election != self.election:
            raise ValidationError("Candidate does not belong to this election.")


class spoiled_votes(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='spoiled_votes')
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('election', 'voter')  # Prevent double reporting
        ordering = ['-timestamp']

    def __str__(self):
        return f"Spoiled vote in {self.election.name} by {self.voter.first_name} {self.voter.last_name} of admission number {self.voter.admission_number}"   

# User  = settings.AUTH_USER_MODEL
# class VotingID(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="voting_ids")
#     election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="voting_ids")
#     code = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField()
#     used = models.BooleanField(default=False)

#     def is_valid(self):
#         return (not self.used) and (self.expires_at > timezone.now())


# def generate_voting_id(user, election):
#     expiry_time = election.end_datetime  # Expire when election ends
#     voting_id = VotingID.objects.create(
#         user=user,
#         election=election,
#         expires_at=expiry_time
#     )
#     return voting_id.code