from django.db import models
from django.contrib.auth.models import User


class NotDeletedDweetManager(models.Manager):
    def get_queryset(self):
        base_queryset = super(NotDeletedDweetManager, self).get_queryset()
        return base_queryset.filter(deleted=False)


class Dweet(models.Model):
    code = models.TextField()
    posted = models.DateTimeField()
    reply_to = models.ForeignKey("self", on_delete=models.DO_NOTHING,
                                 null=True, blank=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name="liked")
    hotness = models.FloatField(default=1.0)
    deleted = models.BooleanField(default=False)

    objects = NotDeletedDweetManager()
    with_deleted = models.Manager()

    def delete(self):
        self.deleted = True
        self.save()

    def __unicode__(self):
        return 'd/' + str(self.id) + ' (' + self.author.username + ')'

    class Meta:
        ordering = ('-posted',)


class Comment(models.Model):
    text = models.TextField()
    posted = models.DateTimeField()
    reply_to = models.ForeignKey(Dweet, on_delete=models.CASCADE,
                                 related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __unicode__(self):
        return ('c/' +
                str(self.id) +
                ' (' +
                self.author.username +
                ') to ' +
                str(self.reply_to))

    class Meta:
        ordering = ('-posted',)
