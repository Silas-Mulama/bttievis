from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from authentication.models import CustomUser, AuditLog
from authentication.forms import SignUpForm,OTPForm

def is_admin(user):
    return user.is_authenticated and user.is_staff

# redirect to admin login if not admin
@login_required
@user_passes_test(is_admin, login_url='admin_login')
def manage_users(request):
    query = request.GET.get("q", "")
    users = CustomUser.objects.all()
    if query:
        users = users.filter(username__icontains=query) | users.filter(email__icontains=query)

    recent_logs = AuditLog.objects.all().order_by('-created_at')[:10]

    return render(request, "adminsite/users.html", {
        "users": users,
        "recent_logs": recent_logs
    })

@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_dashboard(request):
    query = request.GET.get("q", "")
    users = CustomUser.objects.all()
    if query:
        users = users.filter(username__icontains=query) | users.filter(email__icontains=query)

    recent_logs = AuditLog.objects.all().order_by('-created_at')[:10]
    return render(request, "adminsite/dashboard.html", {
        "users": users,
        "recent_logs": recent_logs
    })
    
@login_required
@user_passes_test(is_admin, login_url='admin_login')
def audit_logs(request):
    query = request.GET.get("q", "")
    logs = AuditLog.objects.all().order_by('-created_at')

    if query:
        logs = logs.filter(
            action__icontains=query
        )  | logs.filter(
            ip_address__icontains=query
        ) | logs.filter(
            user__username__icontains=query
        )

    return render(request, "adminsite/auditlogs.html", {"logs": logs})


# admin login view
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        from django.contrib.auth import authenticate, login
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            from django.contrib import messages
            messages.error(request, "Invalid credentials or not an admin user.")
            return redirect('admin_login')
  
    return render(request, "adminsite/admin_login.html")

# add user view
def add_user(request):
    if request.method == 'POST':
        form = SignUpForm
    