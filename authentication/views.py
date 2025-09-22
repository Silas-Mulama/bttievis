from django.shortcuts import render
from django.utils.timezone import now
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate,logout
from .forms import SignUpForm,OTPForm
from .models import otp,AdmissionNumber,CustomUser,VotingID,AuditLog
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import time

# Create your views here.
# audit log views
def log_action(user, action, description, request=None):
    ip = None
    device = None
    if request:
        ip = get_client_ip(request)
        device = request.META.get('HTTP_USER_AGENT', '')

    AuditLog.objects.create(
        user=user,
        action=action,
        description=description,
        ip_address=ip,
        device_info=device
    )

# Helper function to get client IP
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

# get a voting ID
def get_voting_id(request):
    if not request.user.is_authenticated:
        return redirect('login-user')
    
    try:
        # create or get existing voting ID
        voting_id_obj, created = VotingID.objects.get_or_create(user=request.user)
        voting_id = voting_id_obj.voting_id
          
    except Exception as e:
        voting_id = None

    return render(request, 'authentication/voting_id.html', {'voting_id': voting_id})


# verify voting ID
def verify_voting_id(request):
    if request.method == "POST":
        entered_id = request.POST.get("voting_id")
        # Check if the ID exists
        try:
            voting_id_obj = VotingID.objects.get(voting_id=entered_id)
            # Check if ID belongs to logged-in user
            if voting_id_obj.user != request.user:
                messages.error(request, "This Voting ID does not belong to you.")
                return redirect('verify_voting_id')
            messages.success(request, f"Voting ID {entered_id} is valid!")
            return redirect('elections')  # Redirect after success

        except VotingID.DoesNotExist:
            messages.error(request, "Invalid Voting ID. Please try again.")
            return redirect('verify_voting_id')
    # Handle GET request (show form)

    return render(request, 'authentication/verify_voting_id.html')

# register user
def register_user(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        admission_numbers = [num.admission_number for num in AdmissionNumber.objects.all()]

        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data["password1"])
            new_user.admission_number = form.cleaned_data["admission_number"]

            # Email already exists
            if CustomUser.objects.filter(email=new_user.email).exists():
                form.add_error('email', 'Email address is already in use.')
                return render(request, 'authentication/signup.html', {"form": form})

            # Admission number must exist
            if new_user.admission_number not in admission_numbers:
                form.add_error('admission_number', 'The admission number is not recognized.')
                return render(request, 'authentication/signup.html', {"form": form})

            # Admission number must match name
            admission_record = AdmissionNumber.objects.get(admission_number=new_user.admission_number)
            full_name = f"{new_user.first_name} {new_user.last_name}".strip()
            if admission_record.full_name and admission_record.full_name != full_name:
                form.add_error('admission_number', 'Admission number does not match the provided name.')
                return render(request, 'authentication/signup.html', {"form": form})

            # Admission number uniqueness
            if CustomUser.objects.filter(admission_number=new_user.admission_number).exists():
                form.add_error('admission_number', 'This admission number is already registered.')
                return render(request, 'authentication/signup.html', {"form": form})

            # User inactive until OTP verified
            new_user.is_active = False
            new_user.is_verified = False
            new_user.save()

            # Logs
            log_action(new_user, 'User Registration', f'New user registered: {new_user.username}', request)

            # Generate OTP
            otpCode = otp.objects.create(user=new_user)

            # Send OTP via email
            send_mail(
                'Your OTP Code',
                f'Hello {new_user.first_name},\n\nYour Registration OTP code is: {otpCode.code}\n\nThis code is valid for 5 minutes.',
                settings.DEFAULT_FROM_EMAIL,
                [new_user.email],
                fail_silently=False,
            )

            request.session['pending_user_id'] = new_user.id
            return redirect("otp_verification")

    else:
        form = SignUpForm()

    return render(request, 'authentication/signup.html', {"form": form})

def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            request.session['pending_user_id'] = user.id

            # Invalidate old OTPs & send a new one
            otp.objects.filter(user=user, is_used=False).update(is_used=True)
            otpCode = otp.objects.create(user=user)

            send_mail(
                "Your OTP Code",
                f"Hello {user.first_name},\n\nYour OTP code is: {otpCode.code}\n\nThis code is valid for 5 minutes.",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            messages.info(request, "An OTP has been sent to your email.")
            return redirect("otp_verification")
        else:
            return render(request, 'authentication/login.html', {"error": "Invalid username or password"})

    return render(request, 'authentication/login.html')

def otp_verification(request):
    if request.method == "POST":
        code_entered = request.POST.get("otp")
        user_id = request.session.get("pending_user_id")

        if not user_id:
            return redirect("login-user")

        user = CustomUser.objects.get(id=user_id)
        otp_obj = otp.objects.filter(user=user, is_used=False).order_by('-created_at').first()

        if not otp_obj:
            return render(request, "authentication/otp.html", {"error": "No valid OTP found."})

        if otp_obj.created_at < now() - timedelta(minutes=5):
            return render(request, "authentication/otp.html", {"error": "OTP has expired. Please log in again."})

        if otp_obj.code == code_entered:
            user.is_verified = True
            user.is_active = True
            user.save()

            otp_obj.is_used = True
            otp_obj.save()

            del request.session["pending_user_id"]

            login(request, user)
            log_action(user, 'User Login', f'User logged in: {user.username}', request)

            return redirect("home")
        else:
            return render(request, "authentication/otp.html", {"error": "Invalid OTP"})

    return render(request, "authentication/otp.html")

def resent_otp(request):
    user_id = request.session.get("pending_user_id")
    if not user_id:
        return redirect("login-user")

    user = CustomUser.objects.get(id=user_id)

    otp.objects.filter(user=user, is_used=False).update(is_used=True)
    otpCode = otp.objects.create(user=user)

    send_mail(
        "Your OTP Code",
        f"Hello {user.first_name},\n\nYour OTP code is: {otpCode.code}\n\nThis code is valid for 5 minutes.",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

    messages.success(request, "A new OTP has been sent to your email.")
    return redirect("otp_verification")


# logout user
def logout_user(request):
     # logs
    log_action(request.user, 'User Logout', f'User logged out: {request.user.username}', request)
    logout(request)
   
    return redirect('login-user')

# user profile
def profile(request):
    user = request.user
    return render(request,'authentication/user_profile.html',{'user':user})