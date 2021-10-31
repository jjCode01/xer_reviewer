from datetime import datetime
from typing import Any

from xer_parse import Xer, Task
from data.data import changes, updates


def mk_str(val: Any) -> str:
    if isinstance(val, float):
        return f'{val:,.2f}'

    if isinstance(val, int):
        return f'{val:,}'

    if isinstance(val, datetime):
        return f'{val:%d-%b-%Y}'

    return val

def find_relationship_changes(curr_xer: Xer, prev_xer: Xer) -> None:
    changes['relationship']['deleted']['rows'] = [(
        key[0], prev_xer.tasks[rel['pred_task_id']]['task_name'],
        key[1], prev_xer.tasks[rel['task_id']]['task_name'],
        rel['pred_type'].lstrip('PR_'), mk_str(int(rel['lag_hr_cnt'] / 8)))
        for key, rel in prev_xer.relationships.items()
        if not key in curr_xer.relationships
    ]

    changes['relationship']['added']['rows'] = []
    changes['relationship']['revised']['rows'] = []

    for key, rel in curr_xer.relationships.items():
        if not key in prev_xer.relationships:
            changes['relationship']['added']['rows'].append((
                key[0], curr_xer.tasks[rel['pred_task_id']]['task_name'],
                key[1], curr_xer.tasks[rel['task_id']]['task_name'],
                rel['pred_type'].lstrip('PR_'),
                mk_str(int(rel['lag_hr_cnt'] / 8))
            ))
            continue

        if var := rel['lag_hr_cnt'] - prev_xer.relationships[key]['lag_hr_cnt']:
            changes['relationship']['revised']['rows'].append((
                key[0], curr_xer.tasks[rel['pred_task_id']]['task_name'],
                key[1], curr_xer.tasks[rel['task_id']]['task_name'],
                rel['pred_type'].lstrip('PR_'), mk_str(int(rel['lag_hr_cnt'] / 8)),
                mk_str(int(prev_xer.relationships[key]['lag_hr_cnt'] / 8)),
                mk_str(int(var / 8))
            ))


def find_resource_changes(curr_xer: Xer, prev_xer: Xer) -> None:
    changes['resource']['deleted']['rows'] = [(
        key[0], prev_xer.get_task(res)['task_name'],
        key[1], mk_str(res['target_qty']), mk_str(res['target_cost']))
        for key, res in prev_xer.resources.items()
        if not key in curr_xer.resources
    ]

    changes['resource']['added']['rows'] = []
    changes['resource']['cost']['rows'] = []
    changes['resource']['unit']['rows'] = []

    for key, res in curr_xer.resources.items():
        if not key in prev_xer.resources:
            changes['resource']['added']['rows'].append((
                key[0], curr_xer.get_task(res)['task_name'],
                key[1], mk_str(res['target_qty']), mk_str(res['target_cost'])
            ))
            continue

        if var := res['target_cost'] - prev_xer.resources[key]['target_cost']:
            changes['resource']['cost']['rows'].append((
                key[0], curr_xer.get_task(res)['task_name'],
                key[1], mk_str(res['target_cost']), mk_str(prev_xer.resources[key]['target_cost']), mk_str(var)
            ))

        if var := res['target_qty'] - prev_xer.resources[key]['target_qty']:
            changes['resource']['unit']['rows'].append((
                key[0], curr_xer.get_task(res)['task_name'],
                key[1], mk_str(res['target_qty']), mk_str(prev_xer.resources[key]['target_qty']), mk_str(var)
            ))

    
def find_task_changes(curr_xer: Xer, prev_xer: Xer) -> None:
    curr_tasks = {task['task_code']: task for task in curr_xer.tasks.values()}
    prev_tasks = {task['task_code']: task for task in prev_xer.tasks.values()}

    changes['task']['deleted']['rows'] = [
        (task['task_code'], task['task_name']) 
        for id, task in prev_tasks.items()
        if not id in curr_tasks
    ]

    changes['task']['added']['rows'] = []
    changes['task']['name']['rows'] = []
    changes['task']['duration']['rows'] = []
    changes['task']['calendar']['rows'] = []
    changes['task']['start']['rows'] = []
    changes['task']['finish']['rows'] = []
    updates['started']['rows'] = []
    # updates['finished']['rows'] = []
    updates['in_progress']['rows'] = []

    for task in curr_tasks.values():
        if not task['task_code'] in prev_tasks:
            changes['task']['added']['rows'].append((
                task['task_code'], task['task_name']
            ))
            continue

        prev = prev_tasks[task['task_code']]

        # task name changes
        if task['task_name'] != prev['task_name']:
            changes['task']['name']['rows'].append((
                task['task_code'], task['task_name'], prev['task_name']
            ))

        # original duration changes
        curr_dur = int(task['target_drtn_hr_cnt'] / 8)
        curr_rem_dur = int(task['remain_drtn_hr_cnt'] / 8)
        prev_dur = int(prev['target_drtn_hr_cnt'] / 8)
        prev_rem_dur = int(prev['remain_drtn_hr_cnt'] / 8)
        if var := curr_dur - prev_dur:
            changes['task']['duration']['rows'].append((
                task['task_code'], task['task_name'], curr_dur, prev_dur, var
            ))

        # calendar changes
        if curr_xer.task_calendar(task) != prev_xer.task_calendar(prev):
            changes['task']['calendar']['rows'].append((
                task['task_code'], task['task_name'],
                curr_xer.task_calendar(task)['clndr_name'],
                prev_xer.task_calendar(prev)['clndr_name']
            ))

        # actual start change
        if not task.not_started and not prev.not_started:
            if task['act_start_date'] != prev['act_start_date']:
                changes['task']['start']['rows'].append((
                    task['task_code'], task['task_name'],
                    mk_str(task['act_start_date']), mk_str(prev['act_start_date'])
                ))

        # actual finish change
        elif task.completed and prev.completed:
            if task['act_end_date'] != prev['act_end_date']:
                changes['task']['finish']['rows'].append((
                    task['task_code'], task['task_name'],
                    mk_str(task['act_finish_date']), mk_str(prev['act_finish_date'])
                ))

        # activity started
        if (task.in_progress and prev.not_started) or (task.completed and not prev.completed):
            updates['started']['rows'].append((
                task['task_code'], task['task_name'],
                mk_str(curr_dur), mk_str(curr_rem_dur),
                mk_str(task.start), mk_str(task.finish), task.status
            ))

        # # activity finished
        # if task.completed and not prev.completed:
        #     updates['finished']['rows'].append((
        #         task['task_code'], task['task_name'],
        #         mk_str(task.start), mk_str(prev.start),
        #         mk_str(task.finish), mk_str(prev.finish)
        #     ))

        # in progress updates
        if task.in_progress and prev.in_progress:
            if curr_rem_dur != prev_rem_dur:
                updates['in_progress']['rows'].append((
                    task['task_code'], task['task_name'],
                    mk_str(curr_dur), mk_str(curr_rem_dur), mk_str(prev_rem_dur),
                    mk_str(task.start), mk_str(task.finish), mk_str(prev.finish)
                ))
