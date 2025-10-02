from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Petition, PetitionVote
from django.shortcuts import get_object_or_404

@login_required
def create_petition(request):
    if request.method == 'POST':
        Petition.objects.create(
            movie_title=request.POST['movie_title'],
            petition_text=request.POST.get('petition_text', ''),
            user=request.user,
        )
        return redirect('petition.create')
    petitions = Petition.objects.order_by('-created_at')
    user_voted_ids = set(
        PetitionVote.objects.filter(user=request.user, petition__in=petitions)
        .values_list('petition_id', flat=True)
    )
    return render(request, 'petition/create_petition.html', {
        'petitions': petitions,
        'user_voted_ids': user_voted_ids,
    })

@login_required
def vote_petition(request, id):
    petition = get_object_or_404(Petition, id=id)
    if request.method == 'POST':
        vote, created = PetitionVote.objects.get_or_create(petition=petition, user=request.user)
        if created:
            petition.votes += 1
            petition.save()
        else:
            vote.delete()
            petition.votes = max(0, petition.votes - 1)
            petition.save()
        return redirect('petition.create')