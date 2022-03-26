from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        labels = {
            "text": "Текст поста",
            "group": "Group",
            "image": "Картинка поста",
        }
        help_texts = {
            "text": "Текст нового поста",
            "group": "Группа, к которой будет относиться пост",
            "image": "Картинка, которая будет в посте",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        labels = {
            "text": "Текст комментария",
        }
        help_texts = {
            "text": "Напишите текст нового комментария",
        }
