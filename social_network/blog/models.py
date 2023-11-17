from django.contrib.auth.models import AbstractUser
from djongo import models
from django.utils.timezone import now
import uuid
from neomodel import StructuredNode, StringProperty


# Простий вузол для побудови графа (username доданий для зручності у нереляційних базах днаих є проблема з цим щоб не потрібно було чіпати Mongo лишній раз)
class CustomUserNode(StructuredNode):
    username = StringProperty(unique_index=True, required=True) 
    userId = StringProperty(unique_index=True, required=True)


class CustomUser(AbstractUser):
    userId = models.UUIDField(default=uuid.uuid4, editable=True, unique=True, primary_key=True)
    email = models.EmailField(unique=True)
    post_count = models.IntegerField(default=0)
    def __str__(self):
        return self.username
 

class FriendShipRelations(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    requestId = models.UUIDField(default=uuid.uuid4, editable=True, unique=True, primary_key=True)
    senderId = models.UUIDField()
    sender_username = models.CharField(max_length=50)
    receiverId = models.UUIDField()
    receiver_username = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def create_neo4j_relationship(self):
        sender_node = CustomUserNode.nodes.get(userId=str(self.sender.userId))
        receiver_node = CustomUserNode.nodes.get(userId=str(self.receiver.userId))

        if self.status == 'pending':
            sender_node.sent_requests.connect(receiver_node, {'status': 'pending'})  # Односторонній звязок для Followers
        elif self.status == 'accepted':
            sender_node.sent_requests.connect(receiver_node, {'status': 'accepted'}) # Двосторонній звязок при прийнятому запиті
            receiver_node.sent_requests.connect(sender_node, {'status': 'accepted'})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.create_neo4j_relationship()  #Переписаний метод для зберігання FriendShipRelations 


class Post(models.Model):
    postId = models.UUIDField(default=uuid.uuid4, editable=True, unique=True, primary_key=True)
    title = models.CharField(max_length=50)
    content = models.TextField(max_length=5000)
    created_date = models.DateTimeField(default=now, editable=False)
    views = models.IntegerField(default=0)
    authors = models.CharField(max_length=100, blank=False)

    def __str__(self):
         return self.title


class Comment(models.Model):
    commentId = models.UUIDField(default=uuid.uuid4, editable=True, unique=True, primary_key=True)
    commented_post = models.UUIDField()
    commented_by = models.CharField(max_length=100)
    content = models.TextField(max_length=3000)


class Like(models.Model):
    likeId = models.UUIDField(default=uuid.uuid4, editable=True, unique=True, primary_key=True)
    liked_objId = models.UUIDField()
    who_likedId = models.UUIDField()
