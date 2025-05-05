from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Max, F, OuterRef, Subquery
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

from .models import Conversation, Message, Connection
from .forms import MessageForm, ConnectionRequestForm

User = get_user_model()

@login_required
def inbox(request):
    """View for displaying user's message inbox."""
    # Get all conversations for the current user
    conversations = Conversation.objects.filter(participants=request.user)

    # Annotate conversations with unread message count and last message info
    conversations = conversations.annotate(
        unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)),
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')

    # Prepare conversation data for the template
    conversation_data = []
    for conversation in conversations:
        other_user = conversation.get_other_participant(request.user)
        last_message = conversation.get_last_message()

        if other_user and last_message:
            conversation_data.append({
                'conversation': conversation,
                'other_user': other_user,
                'last_message': last_message,
                'unread_count': conversation.unread_count
            })

    context = {
        'conversation_data': conversation_data,
        'active_tab': 'inbox'
    }

    return render(request, 'messages/inbox.html', context)

@login_required
def conversation_detail(request, conversation_id):
    """View for displaying a specific conversation."""
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    other_user = conversation.get_other_participant(request.user)

    # Mark all messages from the other user as read
    Message.objects.filter(conversation=conversation, sender=other_user, is_read=False).update(is_read=True)

    # Get all messages in the conversation
    messages_list = conversation.messages.all()

    # Handle new message form
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()

            # Update conversation's updated_at timestamp
            conversation.save()

            # If it's an AJAX request, return the new message as JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': {
                        'content': message.content,
                        'created_at': message.created_at.strftime('%b %d, %Y, %I:%M %p'),
                        'is_sender': True
                    }
                })

            # Otherwise redirect to the conversation
            return redirect('messages:conversation_detail', conversation_id=conversation.id)
    else:
        form = MessageForm()

    context = {
        'conversation': conversation,
        'other_user': other_user,
        'messages_list': messages_list,
        'form': form,
        'active_tab': 'inbox'
    }

    return render(request, 'messages/conversation_detail.html', context)

@login_required
def new_conversation(request, user_id):
    """View for starting a new conversation with a user."""
    other_user = get_object_or_404(User, id=user_id)

    # Check if a conversation already exists between these users
    existing_conversation = Conversation.objects.filter(participants=request.user).filter(participants=other_user).first()

    if existing_conversation:
        return redirect('messages:conversation_detail', conversation_id=existing_conversation.id)

    # Create a new conversation
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, other_user)

            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()

            messages.success(request, _('Message sent successfully!'))
            return redirect('messages:conversation_detail', conversation_id=conversation.id)
    else:
        form = MessageForm()

    context = {
        'form': form,
        'other_user': other_user,
        'active_tab': 'inbox'
    }

    return render(request, 'messages/new_conversation.html', context)

@login_required
def connections(request):
    """View for displaying user's connections."""
    # Get all accepted connections
    user_connections = Connection.objects.filter(
        (Q(sender=request.user) | Q(receiver=request.user)) & Q(status='accepted')
    )

    # Get all pending connection requests
    pending_requests = Connection.objects.filter(receiver=request.user, status='pending')

    # Get all sent connection requests
    sent_requests = Connection.objects.filter(sender=request.user, status='pending')

    context = {
        'connections': user_connections,
        'pending_requests': pending_requests,
        'sent_requests': sent_requests,
        'active_tab': 'connections'
    }

    return render(request, 'messages/connections.html', context)

@login_required
def send_connection_request(request, user_id):
    """View for sending a connection request to a user."""
    receiver = get_object_or_404(User, id=user_id)

    # Check if a connection already exists
    existing_connection = Connection.objects.filter(
        (Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user))
    ).first()

    if existing_connection:
        if existing_connection.status == 'accepted':
            messages.info(request, _('You are already connected with this user.'))
        elif existing_connection.status == 'pending':
            if existing_connection.sender == request.user:
                messages.info(request, _('You have already sent a connection request to this user.'))
            else:
                messages.info(request, _('This user has already sent you a connection request.'))
        else:
            messages.info(request, _('A connection request was previously rejected.'))

        return redirect('accounts:profile_detail', user_id=receiver.id)

    # Handle the connection request form
    if request.method == 'POST':
        form = ConnectionRequestForm(request.POST)
        if form.is_valid():
            connection = Connection.objects.create(sender=request.user, receiver=receiver)

            # If a message was included, create a conversation and send the message
            if form.cleaned_data.get('message'):
                conversation = Conversation.objects.create()
                conversation.participants.add(request.user, receiver)

                Message.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    content=form.cleaned_data['message']
                )

            messages.success(request, _('Connection request sent successfully!'))
            return redirect('accounts:profile_detail', user_id=receiver.id)
    else:
        form = ConnectionRequestForm()

    context = {
        'form': form,
        'receiver': receiver
    }

    return render(request, 'messages/send_connection_request.html', context)

@login_required
@require_POST
def accept_connection(request, connection_id):
    """View for accepting a connection request."""
    connection = get_object_or_404(Connection, id=connection_id, receiver=request.user, status='pending')

    if connection.accept():
        messages.success(request, _('Connection request accepted!'))
    else:
        messages.error(request, _('Failed to accept connection request.'))

    return redirect('messages:connections')

@login_required
@require_POST
def reject_connection(request, connection_id):
    """View for rejecting a connection request."""
    connection = get_object_or_404(Connection, id=connection_id, receiver=request.user, status='pending')

    if connection.reject():
        messages.success(request, _('Connection request rejected.'))
    else:
        messages.error(request, _('Failed to reject connection request.'))

    return redirect('messages:connections')
