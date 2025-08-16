from django.conf import settings
from django.db import models

class Bookmark(models.Model):
  id=models.AutoField(primary_key=True)

  user=models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="bookmarks",
    db_column="user_id",
  )

  room=models.ForeignKey(
    "rooms.Room",
    on_delete=models.CASCADE,
    related_name="bookmarks",
    db_column="room_id",
  )

  created_at=models.DateTimeField(auto_now_add=True, db_column="created_at")

  class Meta:
    db_table="Bookmark"
    constraints=[
      models.UniqueConstraint(fields=["user","room"], name="uniq_user_room_bookmark"),
    ]
    indexes=[
      models.Index(fields=["user"], name="idx_bookmark_user"),
      models.Index(fields=["room"], name="idx_bookmark_room"),
    ]

    def __str__(self):
      return f"{self.user_id}@{self.room_id}"