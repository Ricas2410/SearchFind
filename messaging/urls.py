from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('new-conversation/<int:user_id>/', views.new_conversation, name='new_conversation'),
    path('connections/', views.connections, name='connections'),
    path('send-connection-request/<int:user_id>/', views.send_connection_request, name='send_connection_request'),
    path('accept-connection/<int:connection_id>/', views.accept_connection, name='accept_connection'),
    path('reject-connection/<int:connection_id>/', views.reject_connection, name='reject_connection'),
]
