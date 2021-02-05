from django.http import HttpResponseRedirect,HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view,renderer_classes

from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Choice, Question
from .serializers import QuestionListPageSerializer, QuestionDetailPageSerializer, ChoiceSerializer, VoteSerializer, QuestionResultPageSerializer




class questions_view(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


@api_view(['GET', 'POST'])
def questions_apiview(request):
    if request.method == 'GET':
        questions = Question.objects.all()
        serializer = QuestionListPageSerializer(questions, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = QuestionListPageSerializer(data=request.data)
        if serializer.is_valid():
            question = serializer.save()
            return Response(QuestionListPageSerializer(question).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))




@api_view(['GET', 'PATCH', 'DELETE'])
def question_detail_view(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'GET':
        serializer = QuestionDetailPageSerializer(question)
        return Response(serializer.data)
    elif request.method == 'PATCH':
        serializer = QuestionDetailPageSerializer(question, data=request.data, partial=True)
        if serializer.is_valid():
            question = serializer.save()
            return Response(QuestionDetailPageSerializer(question).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        question.delete()
        return Response("Question deleted", status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def choices_view(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    serializer = ChoiceSerializer(data=request.data)
    if serializer.is_valid():
        choice = serializer.save(question=question)
        return Response(ChoiceSerializer(choice).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def vote_view(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    serializer = VoteSerializer(data=request.data)
    if serializer.is_valid():
        choice = get_object_or_404(Choice, pk=serializer.validated_data['choice_id'], question=question)
        choice.votes += 1
        choice.save()
        return Response("Voted")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def question_result_view(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    serializer = QuestionResultPageSerializer(question)
    return Response(serializer.data)
