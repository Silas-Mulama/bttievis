from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from elections.models import Election
# Create your views here.
def home(request):
    elections = Election.objects.all()
    return render(request, 'base/home.html', {'elections': elections})

def about(request):
    return render(request, 'base/about.html')

def contact(request):
    # get user inquiries and send email to support team
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # send email to support team
        send_mail(
            f'New Contact Inquiry from {name}',
            f'You have received a new inquiry from {name} ({request.user.email}):\n\n{message}',
            email,  # from email
            [settings.EMAIL_HOST_USER],# support team email
            fail_silently=False,
        )
        return render(request, 'base/contact.html', {'success': True})
    return render(request, 'base/contact.html')


