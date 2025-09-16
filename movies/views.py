from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Like, Report
from django.contrib.auth.decorators import login_required

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    like_count = Like.objects.filter(movie=movie).count()
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    template_data['like_count'] = like_count
    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = Like.objects.filter(movie=movie, user=request.user).exists()
    template_data['user_has_liked'] = user_has_liked
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def like_movie(request, id):
    movie = Movie.objects.get(id=id)
    like_count = Like.objects.filter(movie=movie).count()
    
    if request.method == 'POST':
        existing_like = Like.objects.filter(movie=movie, user=request.user).first()
        if existing_like:
            existing_like.delete()
        else:
            like = Like()
            like.movie = movie
            like.user = request.user
            like.save()
        return redirect('movies.show', id=id)
    else:
        template_data = {}
        template_data['title'] = 'Like Movie'
        template_data['like_count'] = like_count
        return render(request, 'movies/like_button.html', {'template_data': template_data})
    
@login_required
def report_comment(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Report Comment'
        template_data['review'] = review
        return render(request, 'movies/report_comment.html', {'template_data': template_data})
    elif request.method == 'POST':
        report = Report()
        report.review = review
        report.user = request.user
        report.reason = request.POST['report_reason']
        report.additional_info = request.POST.get('additional_info', '')
        report.save()
        # Delete the reported comment
        review.delete()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)