import logging
import json

import requests
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from responder.models import Count

logger = logging.getLogger(__name__)

POST_URL = 'https://api.groupme.com/v3/bots/post'

INSULTS_URL = 'http://www.insultgenerator.org'


def send_message(message, attachment_url=None):
    # Build up the response
    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        'bot_id': settings.BOT_ID,
        'text': message,
    }

    if attachment_url:
        data['attachments'] = [
            {
                'type': 'image',
                'url': attachment_url,
            }
        ]

    # We don't really care about the response of this - it always returns a 202
    requests.post(POST_URL, headers=headers, data=json.dumps(data))


def get_insult():
    r = requests.get(INSULTS_URL)

    spl = r.text.split('<TD>')[1]

    return spl.split('</TD>')[0].strip()

@csrf_exempt
@require_http_methods(['GET', 'POST'])
def respond(request):
    post_data = json.loads(request.body)

    if post_data['name'] != 'sinfoniabot':
        # only respond if we weren't the sender
        message = ''

        args = post_data['text'].split(' ')

        if 'triathlon' in post_data['text'].lower():
            message = 'Shut up Cole'
        elif args[0].lower() == 'insult':
            message = '{0} - {1}'.format(args[1], get_insult())
        else:
            c = Count.objects.all()

            if len(c) == 0:
                c = Count.objects.create(count=Count.MAX_COUNT)
            else:
                c = c[0]

            if c.count <= 0:
                # Send if we've reached MAX_COUNT messages
                c.count = Count.MAX_COUNT

                message = get_insult()

            logger.debug('{0} more until next insult'.format(c.count))
            c.count -= 1
            c.save()

        send_message(message)

    return HttpResponse(status=204)
