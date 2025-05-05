from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Conversation(models.Model):
    """Model for conversations between users."""
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conversation {self.id} between {', '.join([str(p) for p in self.participants.all()])}"

    def get_other_participant(self, user):
        """Get the other participant in a conversation."""
        return self.participants.exclude(id=user.id).first()

    def get_last_message(self):
        """Get the last message in a conversation."""
        return self.messages.order_by('-created_at').first()

class Message(models.Model):
    """Model for messages within a conversation."""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def mark_as_read(self):
        """Mark a message as read."""
        if not self.is_read:
            self.is_read = True
            self.save()

class Connection(models.Model):
    """Model for connections between users (similar to LinkedIn connections)."""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
    )

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_connections')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_connections')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sender', 'receiver')
        ordering = ['-created_at']

    def __str__(self):
        return f"Connection from {self.sender} to {self.receiver} ({self.get_status_display()})"

    def accept(self):
        """Accept a connection request."""
        if self.status == 'pending':
            self.status = 'accepted'
            self.save()

            # Create a conversation between the users if it doesn't exist
            conversation, created = Conversation.objects.get_or_create()
            conversation.participants.add(self.sender, self.receiver)

            return True
        return False

    def reject(self):
        """Reject a connection request."""
        if self.status == 'pending':
            self.status = 'rejected'
            self.save()
            return True
        return False
