from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.db.models import Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from dwitter.models import Dweet
from dwitter.user.forms import UserSettingsForm


def user_settings(request, url_username):
    user = get_object_or_404(User, username=url_username)
    if request.user != user:
        raise Http404

    if request.method == 'POST':
        user_settings_form = UserSettingsForm(request.POST, instance=user)
        if user_settings_form.is_valid():
            user = user_settings_form.save()
            messages.add_message(request, messages.INFO, 'Saved!')
        return redirect('user_settings', url_username=request.user.username)

    return render(request, 'user/settings.html', {
        'user': user,
        'settings_form': UserSettingsForm(instance=user)
    })


def user_feed(request, url_username, page_nr, sort):
    user = get_object_or_404(User, username=url_username)
    page = int(page_nr)
    dweets_per_page = 10
    first = (page - 1) * dweets_per_page
    last = page * dweets_per_page
    dweets = Dweet.objects.filter(author=user)
    dweet_count = dweets.count()
    total_awesome = dweets.annotate(
        num_likes=Count('likes')).aggregate(
            totalaws=Sum('num_likes'))['totalaws']
    if(first < 0 or first >= dweet_count):
        return render(request, 'base.html', {'text': 'No dweets here'})
    if(last >= dweet_count):
        last = dweet_count

    dweet_list = Dweet.objects.filter(author=user)

    if(sort == "top"):
        dweet_list = (dweet_list.annotate(num_likes=Count('likes'))
                      .order_by('-num_likes', '-posted')[first:last])
    elif (sort == "new"):
        dweet_list = dweet_list.order_by('-posted')[first:last]
    elif (sort == "hot"):
        dweet_list = (dweet_list.annotate(num_likes=Count('likes'))
                      .order_by('-num_likes')[first:last])
    else:
        raise Http404("No such sorting method " + sort)

    next_url = reverse('user_feed_page', kwargs={'url_username': url_username,
                                                 'page_nr': page + 1,
                                                 'sort': sort})

    prev_url = reverse('user_feed_page', kwargs={'url_username': url_username,
                                                 'page_nr': page - 1,
                                                 'sort': sort})

    context = {'dweet_list': dweet_list,
               'header_title': url_username + ' (' + str(total_awesome) + ')',
               'feed_type': 'user',
               'feed_user': url_username,
               'page_nr': page,
               'on_last_page': last == dweet_count,
               'next_url': next_url,
               'prev_url': prev_url,
               }
    return render(request, 'feed/feed.html', context)
