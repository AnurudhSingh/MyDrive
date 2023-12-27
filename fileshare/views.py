# fileshare/views.py

from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Folder, File, SharedFile, Notification, UserSettings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate, update_session_auth_hash
from .forms import CustomPasswordChangeForm, CustomUserChangeForm, LoginForm, RegistrationForm, RenameForm, UserPasswordChangeForm, UserSettingsForm
from django.contrib import messages
from django.db.models import QuerySet, Q
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.db import transaction


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        form = RegistrationForm()
        if request.method == 'POST':
                form = RegistrationForm(request.POST)
                if form.is_valid():
                    form.save()
                    user=form.cleaned_data.get('username')
                    messages.success(request, 'Account for ' + user + ' created successfully. Please log in.')
                    return redirect('login')
            # If it's a GET request or the form is not valid, render the registration page
        return render(request, 'registration/register.html', {'form': form})
    
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            form = LoginForm(request, data=request.POST)
            if form.is_valid():  # Fix the typo here
                user = form.get_user()
                login(request, user)
                return redirect('dashboard')
        else:
            form = LoginForm()

        return render(request, 'registration/login.html', {'form': form})
    
def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                    login(request, user)
                    return redirect('dashboard')
            else:
                messages.info(request, 'Username OR Password is incorrect')
        return render(request, 'registration/login.html', {})

def logout_view(request):
    logout(request)
    # Redirect to a specific page after logout
    return redirect('login')

@login_required
def dashboard(request):
    # Get the folders and files associated with the user
    folders = Folder.objects.filter(created_by=request.user, deleted=False)
    files_in_folders = File.objects.filter(folder__created_by=request.user, deleted=False)
    root_files = File.objects.filter(uploaded_by=request.user, folder__isnull=True, deleted=False)

    if request.method == 'POST' and 'file_id' in request.POST:
        file_id = request.POST['file_id']
        file = get_object_or_404(File, id=file_id)

        if file.folder and (file.folder.deleted or file.folder.created_by != request.user):
            # File is either in a deleted folder or not owned by the current user
            return JsonResponse({'status': 'error', 'message': 'Invalid operation'})

        file.starred = not file.starred
        file.save()
        return JsonResponse({'status': 'success'})

    context = {
        'folders': folders,
        'files_in_folders': files_in_folders,
        'root_files': root_files,
    }

    return render(request, 'fileshare/dashboard.html', context)

@login_required
def create_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        folder = Folder.objects.create(name=folder_name, created_by=request.user)
        return redirect('dashboard')

    return render(request, 'fileshare/create_folder.html')

@login_required
def upload_file(request, folder_id=None):
    folder = None

    if folder_id:
        folder = get_object_or_404(Folder, pk=folder_id, created_by=request.user, deleted=False)

    if request.method == 'POST':
        file_name = request.POST.get('file_name')
        uploaded_file = request.FILES['file']

        # If folder is specified, create the file inside the folder; otherwise, create it in the root directory (dashboard)
        if folder:
            file = File.objects.create(name=file_name, folder=folder, uploaded_by=request.user, file=uploaded_file)
            return redirect('view_folder', folder_id=folder.id)
        else:
            # No folder specified, associate the file with the root directory (dashboard)
            file = File.objects.create(name=file_name, uploaded_by=request.user, file=uploaded_file)
            return redirect('dashboard')  # Redirect to the dashboard

    return render(request, 'fileshare/upload_file.html', {'folder': folder})

@login_required
def view_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, created_by=request.user, deleted=False)
    files = File.objects.filter(folder=folder, deleted=False)

    return render(request, 'fileshare/view_folder.html', {'folder': folder, 'files': files})

@login_required
def share(request, item_type, item_id):
    if request.method == 'POST':
        item = get_object_or_404(Folder if item_type == 'folder' else File, pk=item_id)
        usernames = request.POST.get('usernames')
        shared_users = User.objects.filter(username__in=usernames.split(','))

        if item_type == 'folder':
            shared_item, created = SharedFile.objects.get_or_create(folder=item)
        else:
            shared_item, created = SharedFile.objects.get_or_create(file=item)

        shared_item.shared_with.set(shared_users)

        # Record the user who shared the item
        shared_item.shared_by = request.user
        shared_item.save()

        # Notify the shared users
        for shared_user in shared_users:
            Notification.objects.create(
                user=shared_user,
                message=f"You received a {item_type} named '{item.name}' from {request.user.username}."
            )

        return redirect('dashboard')
    
    users = User.objects.all()
    return render(request, 'fileshare/share.html', {'item_type': item_type, 'item_id': item_id, 'users': users})

@login_required
def shared_files(request):
    # Filter out shared files that are not deleted
    shared_files = SharedFile.objects.filter(shared_with=request.user, file__deleted=False)

    # Collect shared file information along with shared time from notifications
    shared_file_info = []
    for shared_file in shared_files:
        # Use the timestamp from the associated notification
        shared_time = Notification.objects.filter(user=request.user, message=f"You received a file named '{shared_file.file.name}' from {shared_file.shared_by.username}").first()
        shared_file_info.append({'shared_file': shared_file, 'shared_time': shared_time.timestamp if shared_time else None})

    return render(request, 'fileshare/shared_files.html', {'shared_file_info': shared_file_info})


@login_required
def settings(request):
    user = request.user

    if request.method == 'POST':
        if 'password_change' in request.POST:
            form = UserPasswordChangeForm(user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Important to prevent logging out
                messages.success(request, 'Your password was successfully updated.')
        else:
            form = UserSettingsForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                
    else:
        form = UserSettingsForm(instance=user)

    password_change_form = UserPasswordChangeForm(user)

    return render(request, 'fileshare/settings.html', {'form': form, 'password_change_form': password_change_form})

@login_required
def rename_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)

    if request.method == 'POST':
        form = RenameForm(request.POST)
        if form.is_valid():
            folder.name = form.cleaned_data['new_name']
            folder.save()
            return redirect('dashboard')  # Redirect to the dashboard
    else:
        form = RenameForm(initial={'new_name': folder.name})

    return render(request, 'fileshare/rename_folder.html', {'form': form, 'folder': folder})

@login_required
def rename_file(request, file_id):
    file = get_object_or_404(File, id=file_id)

    if request.method == 'POST':
        form = RenameForm(request.POST)
        if form.is_valid():
            file.name = form.cleaned_data['new_name']
            file.save()
            return redirect('dashboard')  # Redirect to the dashboard
    else:
        form = RenameForm(initial={'new_name': file.name})

    return render(request, 'fileshare/rename_file.html', {'form': form, 'file': file})

@login_required
def delete_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)

    if request.method == 'POST':
        folder.deleted = True
        folder.deleted_by = request.user  # Set the user who deleted the folder
        folder.deleted_at = timezone.now()
        folder.save()
        return redirect('dashboard')

    return render(request, 'fileshare/confirm_delete.html', {'type': 'folder', 'name': folder.name})

@login_required
def delete_file(request, file_id):
    file = get_object_or_404(File, id=file_id)

    # Check if the file is in a folder that is either deleted or not owned by the current user
    if file.folder and (file.folder.deleted or file.folder.created_by != request.user):
        return JsonResponse({'status': 'error', 'message': 'Invalid operation'})

    if request.method == 'POST':
        # Check if it's a shared file
        if hasattr(file, 'sharedfile') and file.sharedfile.shared_with == request.user:
            shared_file_entry = file.sharedfile

            # Mark the shared file entry as deleted
            shared_file_entry.deleted = True
            shared_file_entry.deleted_by = request.user
            shared_file_entry.deleted_at = timezone.now()
            shared_file_entry.save()

            # Redirect to the shared_files page after deleting the shared file
            return redirect('shared_files')

        # It's the user's own file
        with transaction.atomic():
            # Use atomic transaction to ensure consistency
            if not file.deleted:
                # Move it to the user's trash only if it's not already there
                file.deleted = True
                file.deleted_by = request.user
                file.deleted_at = timezone.now()
                file.save()

        # Redirect to the trash page after deleting the file
        return redirect('trash')

    return render(request, 'fileshare/confirm_delete.html', {'type': 'file', 'name': file.name})

@login_required
def trash(request):
    # Include both folders and files (including root files) that are marked as deleted
    folders = Folder.objects.filter(deleted=True, created_by=request.user)
    files_in_folders = File.objects.filter(deleted=True, folder__created_by=request.user)

    # Include root files that are marked as deleted
    root_files = File.objects.filter(Q(deleted=True, uploaded_by=request.user, folder__isnull=True) | Q(deleted=True, folder__isnull=True, uploaded_by=request.user))

    # Include shared files that were marked as deleted by the current user
    shared_files = SharedFile.objects.filter(file__deleted=True, shared_with=request.user)

    return render(request, 'fileshare/trash.html', {'folders': folders, 'files_in_folders': files_in_folders, 'root_files': root_files, 'shared_files': shared_files, 'nav_folders': Folder.objects.filter(created_by=request.user), 'nav_files': File.objects.filter(folder__created_by=request.user)})

@login_required
def delete_permanently(request, file_id):
    print(f"Attempting to permanently delete file with ID {file_id}")

    try:
        # Check if the file is a shared file
        shared_file_entry = SharedFile.objects.get(file_id=file_id, shared_with=request.user)
        
        # Assuming you want to permanently delete the shared file entry
        shared_file_entry.delete()

    except SharedFile.DoesNotExist:
        # If the file is not a shared file, delete it directly
        file = get_object_or_404(File, id=file_id, uploaded_by=request.user)
        file.delete()

    print(f"File with ID {file_id} permanently deleted")

    # Redirect to the trash or another appropriate page
    return redirect('trash')

@login_required
def restore_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    folder.deleted = False
    folder.save()
    return redirect('trash')

@login_required
def restore_file(request, file_id):
    file = get_object_or_404(File, id=file_id)

    # Check if the file has a folder and if it's owned by the current user
    if file.folder and file.folder.created_by != request.user:
        return JsonResponse({'status': 'error', 'message': 'Invalid operation'})

    # Check if the file is in the root directory (dashboard) and is owned by the current user
    if file.folder is None and file.uploaded_by != request.user:
        return JsonResponse({'status': 'error', 'message': 'Invalid operation'})

    file.deleted = False
    file.save()
    return redirect('trash')


@login_required
def starred(request):
    starred_files = File.objects.filter(starred=True, folder__created_by=request.user, uploaded_by=request.user, deleted=False)
    starred_folders = Folder.objects.filter(starred=True, created_by=request.user, deleted=False)
    
    # Retrieve starred root files
    starred_root_files = File.objects.filter(folder=None, uploaded_by=request.user, starred=True, deleted=False)

    return render(request, 'fileshare/starred.html', {'starred_files': starred_files, 'starred_folders': starred_folders, 'starred_root_files': starred_root_files})


@login_required
def toggle_star(request, file_id):
    file = get_object_or_404(File, id=file_id)

    # Check if the file is in a folder that is either deleted or not owned by the current user
    if file.folder and (file.folder.deleted or file.folder.created_by != request.user):
        return JsonResponse({'status': 'error', 'message': 'Invalid operation'})

    if request.method == 'GET':
        # If it's a shared file, update the shared file's star status
        if hasattr(file, 'sharedfile') and file.sharedfile.shared_with == request.user:
            file.sharedfile.file.starred = not file.sharedfile.file.starred
            file.sharedfile.file.save()
        else:
            # If it's the user's own file, update the file's star status
            file.starred = not file.starred
            file.save()

        if file.folder:
            return redirect('view_folder', folder_id=file.folder.id)
        else:
            return redirect('dashboard')

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required
def untoggle_star(request, file_id):
    file = get_object_or_404(File, id=file_id)

    if file.folder and (file.folder.deleted or file.folder.created_by != request.user):
        # File is either in a deleted folder or not owned by the current user
        return JsonResponse({'status': 'error', 'message': 'Invalid operation'})

    file.starred = not file.starred
    file.save()

    return redirect('dashboard')

def search_files(request):
    query = request.GET.get('q', '')
    
    # Perform search logic here, you might want to search in both folders and files
    folders = Folder.objects.filter(name__icontains=query)
    files = File.objects.filter(name__icontains=query)
    
    return render(request, 'fileshare/search_results.html', {'folders': folders, 'files': files, 'query': query})

