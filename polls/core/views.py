from datetime import datetime, timedelta
import redis
import uuid
from django.http import JsonResponse
from django.views.generic import View
from django.conf import settings


def redis_connection(db=0) -> redis.Redis:
    return redis.Redis(host=settings.REDIS_HOST, db=db, decode_responses=True)


class Poll(View):
    def post(self, request, *args, **kwargs):
        poll_name = request.POST.get('poll_name')
        options = request.POST.get('options').split(';')
        poll_duration_days = int(request.POST.get('poll_duration_days'))
        poll_obj = {'name': poll_name,
                    'open_flag': 1,
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'planned_end_date': (datetime.now() + timedelta(days=poll_duration_days)).strftime('%Y-%m-%d %H:%M:%S'),
                    'options': ';'.join(options),
                    }
        for i, opt in enumerate(options):
            poll_obj[f'option::{i}'] = 0

        poll_id = 'poll::' + uuid.uuid4().hex
        r = redis_connection(db=0)
        r.hset(poll_id, mapping=poll_obj)
        return JsonResponse({'message': 'Poll Created', 'poll_id': poll_id}, status=200)


class Polls(View):
    def get(self, request, *args, **kwargs):
        context = {'polls': []}

        for poll_id in redis_connection(0).scan_iter():
            poll_obj = redis_connection(0).hgetall(poll_id)
            poll_obj['options'] = poll_obj['options'].split(';')
            context['polls'].append(poll_obj)
        # return render(request, 'polls.html', context)
        return JsonResponse(context, status=200)


class Vote(View):
    def post(self, request, *args, **kwargs):
        user_id = request.COOKIES.get('csrftoken')
        poll_id = request.POST.get('poll_id')
        opinion_id = request.POST.get('opinion_id')

        redis_user_poll_key = f'{user_id}::poll::{poll_id}'
        # user db=1
        r1 = redis_connection(db=1)
        if r1.get(redis_user_poll_key):
            return JsonResponse({'message': 'You have already voted'}, status=200)

        # poll db=0
        r0 = redis_connection(db=0)
        open_flag = r0.hget(f'poll::{poll_id}', 'open_flag')
        if open_flag is None:
            return JsonResponse({'message': 'Poll not found'}, status=404)
        if open_flag == 0:
            return JsonResponse({'message': 'Poll is closed'}, status=200)

        r0.hincrby(f'poll::{poll_id}', f'option::{opinion_id}')
        r1.set(redis_user_poll_key, opinion_id)
        return JsonResponse({'message': 'Thank you for your Vote'}, status=200)

