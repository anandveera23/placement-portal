from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Question
from .models import CodingQuestion
from .models import MCQResult
import sys
import io
import time


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def mcq_test(request):
    questions = list(Question.objects.all())

    if not questions:
        return render(request, "mcq_result.html", {
            "score": 0,
            "total": 0
        })

    # Initialize session only once
    if "mcq_index" not in request.session:
        request.session["mcq_index"] = 0
        request.session["mcq_score"] = 0
        request.session["start_time"] = time.time()

    mcq_index = request.session["mcq_index"]
    start_time = request.session.get("start_time")

    # Calculate remaining time
    exam_duration = 30 * 60
    elapsed_time = time.time() - start_time
    remaining_time = int(exam_duration - elapsed_time)

    # Time finished
    if remaining_time <= 0:
        score = request.session["mcq_score"]
        total = len(questions)

        MCQResult.objects.create(
            user=request.user,
            score=score,
            total=total
        )

        request.session.pop("mcq_index", None)
        request.session.pop("mcq_score", None)
        request.session.pop("start_time", None)


        return render(request, "mcq_result.html", {
            "score": score,
            "total": total
        })

    # Finished all questions
    if mcq_index >= len(questions):
        score = request.session["mcq_score"]
        total = len(questions)

        MCQResult.objects.create(
            user=request.user,
            score=score,
            total=total
        )

        request.session.pop("mcq_index", None)
        request.session.pop("mcq_score", None)
        request.session.pop("start_time", None)


        return render(request, "mcq_result.html", {
            "score": score,
            "total": total
        })

    question = questions[mcq_index]

    if request.method == "POST":
        selected = request.POST.get("answer")

        if selected == question.correct_answer:
            request.session["mcq_score"] += 1

        request.session["mcq_index"] += 1
        request.session.modified = True  # IMPORTANT

        return redirect("mcq_test")

    return render(request, "mcq_test.html", {
        "question": question,
        "current": mcq_index + 1,
        "total": len(questions),
        "remaining_time": remaining_time
    })



@login_required
def coding_list(request):
    questions = CodingQuestion.objects.all()
    return render(request, 'coding_list.html', {'questions': questions})

from django.http import JsonResponse
import sys, io
@login_required
def coding_test(request):
    questions = list(CodingQuestion.objects.all())

    if not questions:
        return render(request, "coding_result.html", {
            "score": 0,
            "total": 0
        })

    if "q_index" not in request.session:
        request.session["q_index"] = 0
        request.session["score"] = 0

    q_index = request.session["q_index"]

    # Finished exam
    if q_index >= len(questions):
        score = request.session["score"]
        total = len(questions)
        request.session.flush()
        return render(request, "coding_result.html", {
            "score": score,
            "total": total
        })

    question = questions[q_index]

    # RUN CODE (AJAX)
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        code = request.POST.get("code", "")
        try:
            old_stdout = sys.stdout
            old_stdin = sys.stdin
            sys.stdout = io.StringIO()
            sys.stdin = io.StringIO(question.test_input)

            exec(code, {})

            output = sys.stdout.getvalue().strip()
            sys.stdout = old_stdout
            sys.stdin = old_stdin

            correct = output == question.expected_output.strip()

            return JsonResponse({
                "output": output,
                "correct": correct
            })

        except Exception as e:
            sys.stdout = old_stdout
            sys.stdin = old_stdin
            return JsonResponse({
                "output": str(e),
                "correct": False
            })

    # SUBMIT ANSWER → NEXT QUESTION
    if request.method == "POST":
        if request.POST.get("is_correct") == "true":
            request.session["score"] += 1

        request.session["q_index"] += 1
        return redirect("coding_test")

    return render(request, "coding_test.html", {
        "question": question,
        "current": q_index + 1,
        "total": len(questions)
    })



@login_required
def performance(request):
    results = MCQResult.objects.filter(user=request.user).order_by('-date_taken')

    total_tests = results.count()
    highest_score = max([r.score for r in results], default=0)
    average_score = (
        sum([r.score for r in results]) / total_tests
        if total_tests > 0 else 0
    )

    context = {
        'results': results,
        'total_tests': total_tests,
        'highest_score': highest_score,
        'average_score': round(average_score, 2),
    }

    return render(request, 'performance.html', context)
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Count

@login_required
def leaderboard(request):
    leaderboard_data = (
        MCQResult.objects
        .values('user__username')
        .annotate(
            total_tests=Count('id'),
            best_score=Max('score'),
            avg_score=Avg('score')
        )
        .order_by('-best_score', '-avg_score')
    )

    return render(
        request,
        'leaderboard.html',
        {'leaderboard': leaderboard_data}
    )
@login_required
def all_results(request):
    if not request.user.is_superuser:
        return redirect("dashboard")

    results = MCQResult.objects.all().order_by('-date_taken')

    return render(request, "all_results.html", {
        "results": results
    })
