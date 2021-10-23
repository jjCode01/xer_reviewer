from datetime import datetime
from typing import Any
from dataclasses import dataclass

from xer_parse import Xer, Task

@dataclass
class TaskVar:
    added: list
    deleted: list
    names: list
    orig_durations: list
    calendars: list
    actual_start: list
    actual_finish: list


@dataclass
class RelVar:
    added: list
    deleted: list
    revised: list

@dataclass
class ResVar:
    added: dict[str, list]
    deleted: dict[str, list]
    revised: dict[str, list]


def mk_str(val: Any) -> str:
    if isinstance(val, float):
        return f'{val:,.2f}'

    if isinstance(val, int):
        return f'{val:,}'

    if isinstance(val, datetime):
        return f'{val:%d-%b-%Y}'

    return val

def find_relationship_changes(curr_xer: Xer, prev_xer: Xer) -> RelVar:
    added = {'cols': ['Pred Id', 'Pred Name', 'Succ Id', 'Succ Name', 'Link', 'Lag'], 'rows': []}
    revised = {'cols': ['Pred Id', 'Pred Name', 'Succ Id', 'Succ Name', 'Link', 'New Lag', 'Old Lag', 'Var'], 'rows': []}
    for key, rel in curr_xer.relationships.items():
        if not key in prev_xer.relationships:
            added['rows'].append((
                key[0], curr_xer.tasks[rel['pred_task_id']]['task_name'],
                key[1], curr_xer.tasks[rel['task_id']]['task_name'],
                rel['pred_type'].lstrip('PR_'),
                mk_str(int(rel['lag_hr_cnt'] / 8))
            ))

        elif var := rel['lag_hr_cnt'] - prev_xer.relationships[key]['lag_hr_cnt']:
            revised['rows'].append((
                key[0], curr_xer.tasks[rel['pred_task_id']]['task_name'],
                key[1], curr_xer.tasks[rel['task_id']]['task_name'],
                rel['pred_type'].lstrip('PR_'), mk_str(int(rel['lag_hr_cnt'] / 8)),
                mk_str(int(prev_xer.relationships[key]['lag_hr_cnt'] / 8)),
                mk_str(int(var / 8))
            ))

    deleted = {'cols': ['Pred Id', 'Pred Name', 'Succ Id', 'Succ Name', 'Link', 'Lag'],
               'rows': [(
                    key[0], prev_xer.tasks[rel['pred_task_id']]['task_name'],
                    key[1], prev_xer.tasks[rel['task_id']]['task_name'],
                    rel['pred_type'].lstrip('PR_'), mk_str(int(rel['lag_hr_cnt'] / 8))
                ) for key, rel in prev_xer.relationships.items() if not key in curr_xer.relationships]}

    # s = lambda x: (x[0], x[2])
    return RelVar(added, deleted, revised)


def find_resource_changes(curr_xer: Xer, prev_xer: Xer) -> RelVar:
    added = {'cols': ['Act Id', 'Act Name', 'Resource', 'Budget Units', 'Budget Cost'], 'rows': []}
    revised = {'cols': ['Act Id', 'Act Name', 'Resource', 'New Cost', 'Old Cost', 'Var'], 'rows': []}
    for key, res in curr_xer.resources.items():
        if not key in prev_xer.resources:
            added['rows'].append((
                key[0], curr_xer.get_task(res)['task_name'],
                key[1], mk_str(res['target_qty']), mk_str(res['target_cost'])
            ))

        elif var := res['target_cost'] - prev_xer.resources[key]['target_cost']:
            revised['rows'].append((
                key[0], curr_xer.get_task(res)['task_name'],
                key[1], mk_str(res['target_cost']), prev_xer.resources[key]['target_cost'], mk_str(var)
            ))

    s = lambda x: x[0]
    deleted = {'cols': ['Act Id', 'Act Name', 'Resource', 'Budget Units', 'Budget Cost'], 
               'rows': [(
                    key[0], prev_xer.get_task(res)['task_name'],
                    key[1], mk_str(res['target_qty']), mk_str(res['target_cost'])
                ) for key, res in prev_xer.resources.items() if not key in curr_xer.resources]}

    
    return ResVar(added, deleted, revised)

    
def find_task_changes(curr_xer: Xer, prev_xer: Xer) -> TaskVar:
    curr_tasks = {task['task_code']: task for task in curr_xer.tasks.values()}
    prev_tasks = {task['task_code']: task for task in prev_xer.tasks.values()}

    added = {'cols': ['Act Id', 'Act Name'], 'rows': []}

    deleted = {
        'cols': ['Act Id', 'Act Name'], 
        'rows': [
            (task['task_code'], task['task_name']) 
            for id, task in prev_tasks.items()
            if not id in curr_tasks
        ]
    }

    names = {'cols': ['Act Id', 'New Name', 'Old Name'], 'rows': []}
    orig_durs = {'cols': ['Act Id', 'Act Name', 'New Dur', 'Old Dur', 'Var'], 'rows': []}
    calendars = {'cols': ['Act Id', 'Act Name', 'New Cal', 'Old Cal'], 'rows': []}
    actual_start = {'cols': ['Act Id', 'Act Name', 'New Start', 'Old Start'], 'rows': []}
    actual_finish = {'cols': ['Act Id', 'Act Name', 'New Finish', 'Old Finish'], 'rows': []}

    for task in curr_tasks.values():
        if not task['task_code'] in prev_tasks:
            added['rows'].append((task['task_code'], task['task_name']))
            continue

        prev = prev_tasks[task['task_code']]

        # task name changes
        if task['task_name'] != prev['task_name']:
            names['rows'].append((task['task_code'], task['task_name'], prev['task_name']))

        # original duration changes
        curr_dur = int(task['target_drtn_hr_cnt'] / 8)
        prev_dur = int(prev['target_drtn_hr_cnt'] / 8)
        if var := curr_dur - prev_dur:
            orig_durs['rows'].append((task['task_code'], task['task_name'], curr_dur, prev_dur, var))

        # calendar changes
        if curr_xer.task_calendar(task) != prev_xer.task_calendar(prev):
            calendars['rows'].append((
                task['task_code'],
                task['task_name'],
                curr_xer.task_calendar(task)['clndr_name'],
                prev_xer.task_calendar(prev)['clndr_name']
            ))

        if not task.not_started and not prev.not_started:
            if task['act_start_date'] != prev['act_start_date']:
                actual_start['rows'].append((
                    task['task_code'], task['task_name'],
                    mk_str(task['act_start_date']), mk_str(prev['act_start_date'])
                ))

        if task.completed and prev.completed:
            if task['act_end_date'] != prev['act_end_date']:
                actual_finish['rows'].append((
                    task['task_code'], task['task_name'],
                    mk_str(task['act_end_date']), mk_str(prev['act_end_date'])
                ))

    return TaskVar(added, deleted, names, orig_durs, calendars, actual_start, actual_finish)


def find_added_tasks(curr: list[Task], prev: list[Task]) -> list[Task]:
    return list(set(curr) - set(prev))
