from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

class Folder(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_folders')
    deleted_at = models.DateTimeField(null=True, blank=True)
    starred = models.BooleanField(default=False)
    folder_id = models.IntegerField(default=1)  # Assign a default value for the root directory

    def __str__(self):
        return self.name

class File(models.Model):
    name = models.CharField(max_length=255)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='uploads/')
    deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_files')
    deleted_at = models.DateTimeField(null=True, blank=True)
    starred = models.BooleanField(default=False)

    def toggle_starred(self):
        self.starred = not self.starred
        self.save()

class SharedFile(models.Model):
    file = models.ForeignKey(File, null=True, blank=True, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, null=True, blank=True, on_delete=models.CASCADE)
    shared_with = models.ManyToManyField(User)
    shared_at = models.DateTimeField(null=True, blank=True)
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_files', default=1)
    starred = models.BooleanField(default=False)

    def __str__(self):
        return self.file.name

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add fields for user settings as needed

    def __str__(self):
        return self.user.username
    
