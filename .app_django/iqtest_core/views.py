from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Result
from .utils.problem_loader import load_random_questions


def index(request):
    if request.method == "POST":
        request.session["age"] = int(request.POST.get("age", 35))
        request.session["gender"] = request.POST.get("gender", "other")
        request.session["questions"] = load_random_questions()
        request.session["start_time"] = timezone.now().isoformat()
        return redirect("question", qnum=1)
    return render(request, "iqtest_core/index.html")


def question(request, qnum):
    questions = request.session.get("questions")
    if not questions or qnum > len(questions):
        return redirect("result")
    q = questions[qnum - 1]
    return render(request, "iqtest_core/question.html", {"q": q, "qnum": qnum, "total": len(questions)})


def submit(request, qnum):
    if request.method == "POST":
        selected = request.POST.get("selected")
        questions = request.session.get("questions")
        q = questions[qnum - 1]
        correct = q["answer"]
        is_correct = selected == correct

        Result.objects.create(
            age=request.session.get("age"),
            gender=request.session.get("gender"),
            question_id=q["id"],
            selected=selected,
            correct=correct,
            is_correct=is_correct,
            datetime=timezone.now()
        )
        return redirect("question", qnum=qnum + 1)


def result(request):
    start = timezone.datetime.fromisoformat(request.session.get("start_time"))
    end = timezone.now()
    duration = end - start
    seconds = duration.total_seconds()
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)

    recent_results = Result.objects.order_by('-datetime')[:30]
    if not recent_results:
        correct_percent = 0
    else:
        correct_total = sum(1 for r in recent_results if r.is_correct)
        correct_percent = round(correct_total / len(recent_results) * 100, 1)

    return render(request, "iqtest_core/result.html", {
        "correct_percent": correct_percent,
        "time_minutes": minutes,
        "time_seconds": seconds
    })

