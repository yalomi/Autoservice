from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ReviewForm
from .models import Review
from django.contrib import messages

@login_required
def review_create(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.name = request.user.get_full_name() or request.user.email
            review.save()
            messages.success(request, 'Отзыв успешно добавлен!')
            return redirect('reviews')
    else:
        form = ReviewForm()
    return render(request, 'core/review_form.html', {'form': form, 'action': 'Добавить отзыв'})

@login_required
def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user != request.user:
        messages.error(request, 'Вы не можете редактировать этот отзыв.')
        return redirect('reviews')
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Отзыв успешно обновлён!')
            return redirect('reviews')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'core/review_form.html', {'form': form, 'action': 'Редактировать отзыв'})

@login_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user != request.user:
        messages.error(request, 'Вы не можете удалить этот отзыв.')
        return redirect('reviews')
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Отзыв удалён!')
        return redirect('reviews')
    return render(request, 'core/review_confirm_delete.html', {'review': review}) 