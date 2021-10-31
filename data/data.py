# data.py

updates = {
    'started':{
        'desc': 'Tasks Started',
        'cols': ['Task Id', 'Task Name', 'Orig Dur', 'Rem Dur', 'Start', 'Finish', 'Status'],
        'rows': []
    },
    'finished': {
        'desc': 'Tasks Finished',
        'cols': ['Task Id', 'Task Name', 'Orig Dur', 'Rem Dur', 'Start', 'Finish', 'Status'],
        'rows': []
    },
    'in_progress':{
        'desc': 'In Progress Updates',
        'cols': ['Task Id', 'Task Name', 'Orig Dur', 'Rem Dur', 'Prev Rem Dur', 'Start', 'Finish', 'Prev Finish'],
        'rows': []
    },
}

changes = {
    'task': {
        # 'desc': 'Task Changes',
        'added': {
            'desc': 'Added Tasks',
            'cols': ['Task Id', 'Task Name'],
            'rows': []
        },
        'deleted': {
            'desc': 'Deleted Tasks',
            'cols': ['Task Id', 'Task Name'],
            'rows': []
        },
        'name': {
            'desc': 'Task Name Changes',
            'cols': ['Task Id', 'New Name', 'Old Name'],
            'rows': []
        },
        'duration': {
            'desc': 'Original Duration Changes',
            'cols': ['Task Id', 'Task Name', 'New Dur', 'Old Dur', 'Var'],
            'rows': []
        },
        'calendar': {
            'desc': 'Task Calendar Assignment Changes',
            'cols': ['Task Id', 'Task Name', 'New Cal', 'Old Cal'],
            'rows': []
        },
        'start': {
            'desc': 'Actual Start Date Changes',
            'cols': ['Task Id', 'Task Name', 'New Start', 'Old Start'],
            'rows': []
        },
        'finish': {
            'desc': 'Actual Finish Date Changes',
            'cols': ['Task Id', 'Task Name', 'New Finish', 'Old Finish'],
            'rows': []
        },
    },
    'relationship': {
        # 'desc': 'Relationship Changes',
        'added': {
            'desc': 'Added Relationships',
            'cols': ['Pred Id', 'Pred Name', 'Succ Id', 'Succ Name', 'Link', 'Lag'],
            'rows': []
        },
        'deleted': {
            'desc': 'Deleted Relationships',
            'cols': ['Pred Id', 'Pred Name', 'Succ Id', 'Succ Name', 'Link', 'Lag'],
            'rows': []
        },
        'revised': {
            'desc': 'Revised Relationship Lags',
            'cols': ['Pred Id', 'Pred Name', 'Succ Id', 'Succ Name', 'Link', 'New Lag', 'Old Lag', 'Var'],
            'rows': []
        },
    },
    'resource': {
        # 'desc': 'Resource Changes',
        'added': {
            'desc': 'Added Resource Assignments',
            'cols': ['Task Id', 'Task Name', 'Resource', 'Budget Units', 'Budget Cost'],
            'rows': []
        },
        'deleted': {
            'desc': 'Deleted Resource Assignments',
            'cols': ['Task Id', 'Task Name', 'Resource', 'Budget Units', 'Budget Cost'],
            'rows': []
        },
        'cost': {
            'desc': 'Revised Resource Budgeted Costs',
            'cols': ['Task Id', 'Task Name', 'Resource', 'New Cost', 'Old Cost', 'Var'],
            'rows': []
        },
        'unit': {
            'desc': 'Revised Resource Budgeted Quantities',
            'cols': ['Task Id', 'Task Name', 'Resource', 'New Qty', 'Old Qty', 'Var'],
            'rows': []
        },
    }
}

projects = {
    'current': {},
    'previous': {}
}

activities = {
    'current': {
        'count': 0,
        'not_started': 0,
        'in_progress': 0,
        'completed': 0,
        'longest_path': 0,
    },
    'previous': {
        'count': 0,
        'not_started': 0,
        'in_progress': 0,
        'completed': 0,
        'longest_path': 0,
    }
}

cost_loading = {
    'current': {
        'budget': 0.0,
        'actual': 0.0,
        'this_period': 0.0,
        'remaining': 0.0,
    },
    'previous': {
        'budget': 0.0,
        'actual': 0.0,
        'this_period': 0.0,
        'remaining': 0.0,
    },
}

longest_path = {
    'current': {

    },
    'previous': {

    }
}