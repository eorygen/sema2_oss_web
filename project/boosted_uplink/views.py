import django
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render
from rest_framework import authentication, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from boosted_uplink.models import FeedbackItem, AppUpdateConfig, UplinkConfig


class FeedbackView(APIView):

    def post(self, request):

        user = request.user
        username = request.user.username if request.user else 'unknown'
        user_email = user.email if user is not None else None
        description = request.POST.get('description', '')
        category = request.POST.get('category', 'General')

        item = FeedbackItem(user=user, user_email=user_email, category_name=category, description=description)
        item.save()

        from django.core.mail import send_mail

        # Make sure that no email is sent to a user that actually has
        # a password marked as unusable
        if not user.has_usable_password():
            return HttpResponse(status=404)

        subject = '!! FEEDBACK !!'
        email = 'From: {0}\n\nFeedback: {1}'.format(username, description)

        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = 'contact@boostedhuman.com'

        send_mail(subject, email, from_email, [to_email], fail_silently=False)

        return HttpResponse("OK")


class AppUpdateView(APIView):

    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def post(self, request):

        remote_version = request.DATA.get('build_number')
        remote_platform = request.DATA.get('platform_id')

        try:
            global_config = UplinkConfig.get_uplink_config()

            config = AppUpdateConfig.objects.get(platform_id=remote_platform)

            update_is_available = config.build_number > int(remote_version)

            res = {
                'build_number': config.build_number,
                'update_url': config.update_url,
                'update_is_available': update_is_available
            }

            return Response(res)

        except AppUpdateConfig.DoesNotExist:
            raise Http404

