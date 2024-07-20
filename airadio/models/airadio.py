from django.db import models


class Voice(models.Model):
    name = models.CharField(max_length=255)


class Category(models.Model):
    name = models.CharField(max_length=255)


class Story(models.Model):
    title = models.CharField(max_length=255)
    voice = models.ForeignKey(Voice, on_delete=models.CASCADE)
    intro = models.TextField()
    outro = models.TextField()
    newsbed = models.TextField()
    script_edit = models.TextField()
    categories = models.ManyToManyField(Category, through='StoryCategory')


class StoryCategory(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Soundbyte(models.Model):
    file_path = models.CharField(max_length=255)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
