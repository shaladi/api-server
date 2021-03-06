from django.db import models

# Create your models here.


class UserLogEvent(models.Model):
    time = models.DateTimeField(auto_now=True)
    client = models.CharField(max_length=512)
    event = models.CharField(max_length=1024)
    detail = models.CharField(max_length=1024)


class GcmUser(models.Model):
    user = models.ForeignKey('auth.User')
    gcm_id = models.CharField(max_length=512)


class Item(models.Model):
    """
    An item mentioned in a Reuse email
    """

    #The name of this item
    name = models.CharField(max_length=256)

    #The email address of the person who posted this item
    sender = models.CharField(max_length=64, blank=True)

    #description of item
    description = models.TextField(default="", blank=True)

    #location as XX-XXX string
    location = models.CharField(max_length=256, blank=True, default="")

    #tags as set when item is created
    tags = models.TextField(default="", blank=True)

    #latitude of item as string
    lat = models.TextField(max_length=256, default="", blank=True)

    #longitude of item as string
    lon = models.TextField(max_length=256, default="", blank=True)

    #whether this item was created from an email
    is_email = models.BooleanField(default=False)

    #The NewPostEmail in which this Item was first mentioned
    post_email = models.ForeignKey('NewPostEmail')

    #Whether or not this item has been claimed already (default False)
    claimed = models.BooleanField(default=False)

    #The thread to which this item belongs
    thread = models.ForeignKey('EmailThread', null=True)

    #The last time this item was updated
    modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        ret_val = super(Item, self).save(*args, **kwargs)
        if self.thread and self.thread.modified is None:
            self.thread.modified = self.modified
        elif self.thread:
            self.thread.modified = max(self.thread.modified, self.modified)
        if self.thread:
            self.thread.save()
        return ret_val


class AbstractEmail(models.Model):
    class Meta:
        abstract = True

    #The email address of the person who sent this email
    sender = models.CharField(max_length=64)

    #The subject of the email
    subject = models.CharField(max_length=256)

    #The complete text of the email
    text = models.TextField()

    # The auto_now_add parameter declares that the value of the received field
    # is set to the time the object was created.

    #When the email was received by the server
    received = models.DateTimeField(auto_now_add=True)

    # The auto_now parameter declares that the value of the updated field is set
    # to the time the object was last updated.

    #When the email was last updated
    modified = models.DateTimeField(auto_now=True)

    #The thread this email is a part of
    thread = models.ForeignKey('EmailThread')

    def save(self, *args, **kwargs):
        ret_val = super(AbstractEmail, self).save(*args, **kwargs)
        if self.thread.modified is None:
            self.thread.modified = self.modified
        else:
            self.thread.modified = max(self.thread.modified, self.modified)
        self.thread.save()
        return ret_val
    

class NewPostEmail(AbstractEmail):
    """
    An email with a list of items that have been posted on Reuse
    """

    #Where the posted item(s) is(are) located.
    #Can be a room number, an address, or something else

    location = models.CharField(max_length=256)
    
    def __getattr__(self, name):
        if name== "items":
            return self.item_set.all()
        return super.__getattr__(self, name)

    
class ClaimedItemEmail(AbstractEmail):
    """An email that lists some items as claimed"""
    
    #The items which this email marked as claimed
    items = models.ManyToManyField('Item')


class EmailThread(models.Model):
    """
    A group of one or more emails in the same conversation/thread and the
    associated items.
    """
    
    #The subject of the email thread
    subject = models.CharField(max_length=256)

    # Note that this is not an auto_now field; it can and must be updated
    # manually.
    #When the thread was last updated
    modified = models.DateTimeField(null=True)

    #This id value can be used for sending claimed emails to the same
    #tread by usting its value as "In-Reply-To: <value>" in the email
    #header. Read more here: http://www.rfc-editor.org/rfc/rfc5322.txt
    thread_id = models.CharField(max_length=256, default="", blank=True)



                
