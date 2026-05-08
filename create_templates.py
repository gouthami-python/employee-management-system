import os

templates = {
    'admin/department_list.html': '''{% extends 'base.html' %}
{% block content %}
<h1>Departments</h1>
<a href="{% url 'department_add' %}" class="btn btn-primary mb-3">Add Department</a>
<table class="table">
    <tr><th>Name</th><th>Head</th><th>Employees</th><th>Actions</th></tr>
    {% for dept in departments %}
    <tr>
        <td>{{ dept.name }}</td>
        <td>{{ dept.head|default:"N/A" }}</td>
        <td>{{ dept.employee_count }}</td>
        <td>
            <a href="{% url 'department_edit' dept.pk %}" class="btn btn-sm btn-warning">Edit</a>
            <a href="{% url 'department_delete' dept.pk %}" class="btn btn-sm btn-danger">Delete</a>
        </td>
    </tr>
    {% endfor %}
</table>
{% endblock %}''',
    
    'admin/task_list.html': '''{% extends 'base.html' %}
{% block content %}
<h1>Tasks</h1>
<a href="{% url 'task_assign' %}" class="btn btn-primary mb-3">Assign Task</a>
<table class="table">
    <tr><th>Title</th><th>Assigned To</th><th>Status</th><th>Priority</th><th>Deadline</th></tr>
    {% for task in tasks %}
    <tr>
        <td>{{ task.title }}</td>
        <td>{{ task.assigned_to }}</td>
        <td>{{ task.get_status_display }}</td>
        <td>{{ task.get_priority_display }}</td>
        <td>{{ task.deadline|date:"Y-m-d H:i" }}</td>
    </tr>
    {% endfor %}
</table>
{% endblock %}''',
    
    'employee/dashboard.html': '''{% extends 'base.html' %}
{% block content %}
<h1>Welcome, {{ employee.user.get_full_name }}</h1>
<div class="row">
    <div class="col-md-4">
        <div class="stat-card bg-info text-white">
            <h3>{{ pending_tasks }}</h3>
            <p>Pending Tasks</p>
        </div>
    </div>
    <div class="col-md-4">
        <div class="stat-card bg-success text-white">
            <h3>{{ completed_tasks }}</h3>
            <p>Completed Tasks</p>
        </div>
    </div>
</div>
<h3 class="mt-4">My Tasks</h3>
<table class="table">
    {% for task in my_tasks %}
    <tr>
        <td>{{ task.title }}</td>
        <td>{{ task.get_status_display }}</td>
        <td>{{ task.deadline|date:"Y-m-d" }}</td>
    </tr>
    {% endfor %}
</table>
{% endblock %}''',
}

# Create directories and files
base_dir = 'employees/templates'
for path, content in templates.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(content)
    print(f'Created: {full_path}')