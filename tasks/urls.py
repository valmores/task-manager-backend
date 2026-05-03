from django.urls import path
from .views import (
    TaskListCreateView, TaskDetailView,
    ProjectListCreateView, ProjectDetailView
)

urlpatterns = [
    # Projects
    path('projects/', ProjectListCreateView.as_view(), name='project_list_create'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
    
    # Tasks
    path('', TaskListCreateView.as_view(), name='task_list_create'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
]
