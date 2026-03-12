from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserProfileForm, UserUpdateForm


def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('incident_list')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to UrbanSafe, {user.first_name}! Please complete your profile.')
            return redirect('profile')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Secure user login view."""

    # If user already logged in
    if request.user.is_authenticated:
        return redirect('incident_list')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Django secure authentication
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            messages.success(
                request,
                f"Welcome back, {user.first_name or user.username}!"
            )

            next_url = request.GET.get('next', 'incident_list')
            return redirect(next_url)

        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'accounts/login.html')


def logout_view(request):
    """User logout view."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def profile_view(request):
    """User profile view and edit."""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'incidents_count': request.user.incidents.count(),
        'verifications_count': request.user.verifications.count(),
        'comments_count': request.user.comments.count(),
    }
    return render(request, 'accounts/profile.html', context)
