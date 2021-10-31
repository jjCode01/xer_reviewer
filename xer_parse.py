from collections import defaultdict
from datetime import datetime
from typing import Any


class Calendar:
    def __init__(self, **kwargs) -> None:
        self._kwargs = kwargs

    def __getitem__(self, name: str):
        return self._kwargs[name]

    def __eq__(self, o: object) -> bool:
        return self._kwargs['clndr_name'] == o._kwargs['clndr_name'] and self._kwargs['clndr_type'] == o._kwargs['clndr_type']

    def __hash__(self) -> int:
        return hash((self._kwargs['clndr_name'], self._kwargs['clndr_type']))

    def __str__(self) -> str:
        return f'{self["clndr_name"]} - {self["clndr_type"]}'


class Project:
    def __init__(self, **kwargs) -> None:
        self._kwargs = kwargs

    def __getitem__(self, name: str):
        return self._kwargs[name]

    def __str__(self) -> str:
        return f'{self["proj_short_name"]} - {self["long_name"]}'


class Task:
    STATUS = {
        'TK_NotStart': 'Not Started',
        'TK_Active': 'In Progress',
        'TK_Complete': 'Complete'
    }

    def __init__(self, **kwargs) -> None:
        self._kwargs = kwargs
        self.start = self._kwargs['early_start_date'] \
            if self.not_started \
            else self._kwargs['act_start_date']

        self.finish = self._kwargs['act_end_date'] \
            if self.completed \
            else self._kwargs['early_end_date']

    def __getitem__(self, name: str):
        return self._kwargs[name]

    def __eq__(self, o: object) -> bool:
        return self._kwargs['task_code'] == o._kwargs['task_code']

    def __hash__(self) -> int:
        return hash(self._kwargs['task_code'])

    def __str__(self) -> str:
        return f'{self["task_code"]} - {self["task_name"]}'

    def __getitem__(self, name: str) -> Any:
        return self._kwargs[name]

    @property
    def status(self) -> str:
        return self.STATUS[self._kwargs['status_code']]

    @property
    def in_progress(self) -> bool:
        return self._kwargs['status_code'] == 'TK_Active'

    @property
    def not_started(self) -> bool:
        return self._kwargs['status_code'] == 'TK_NotStart'

    @property
    def completed(self) -> bool:
        return self._kwargs['status_code'] == 'TK_Complete'

    @property
    def longest_path(self) -> bool:
        return self._kwargs['driving_path_flag']

    @property
    def critical(self) -> bool:
        return not self.completed and self._kwargs['total_float_hr_cnt'] <= 0


class Xer:
    def __init__(self, **kwargs) -> None:
        self._kwargs = kwargs
        self.projects = {proj['proj_id']: Project(**proj) for proj in kwargs['PROJECT']}
        self.calendars = {cal['clndr_id']: Calendar(**cal) for cal in kwargs['CALENDAR']}
        self.wbs = {wbs['wbs_id']: wbs for wbs in kwargs['PROJWBS']}
        self.tasks = {task['task_id']: Task(**task) for task in sorted(kwargs['TASK'], key=lambda x: x['task_code'])}

        self.resources = dict()
        for res in sorted(kwargs.get('TASKRSRC', []), key=lambda x: (self.get_task(x)['task_code'], x.get('rsrc_name', None))):
            task = self.get_task(res)['task_code']
            rsrc = res.get('rsrc_name', None)
            self.resources[(task, rsrc)] = res

        self.relationships = dict()
        for rel in sorted(kwargs['TASKPRED'], key=lambda x: (self.get_task(x, 'pred_task_id')['task_code'], self.get_task(x)['task_code'], x['pred_type'])):
            succ = self.get_task(rel)['task_code']
            pred = self.get_task(rel, 'pred_task_id')['task_code']
            link = rel['pred_type']
            self.relationships[(pred, succ, link)] = rel

    def task_calendar(self, task: Task) -> Calendar:
        return self.calendars[task['clndr_id']]

    def get_task(self, obj: object, key='task_id') -> Task:
        return self.tasks[obj[key]]


DATA_TABLES = {
    # 'ACTVCODE': ('actv_code_id', 'actv_code_type_id', 'actv_code_name', 'short_name', 'seq_num', 'total_assignments'),
    # 'ACTVTYPE': ('actv_code_type_id', 'actv_short_len', 'seq_num', 'actv_code_type', 'proj_id', 'wbs_id', 'actv_code_type_scope'),
    'CALENDAR': ('clndr_id', 'default_flag', 'clndr_name', 'proj_id', 'base_clndr_id', 'clndr_type', 'clndr_data'),
    # 'FINDATES': ('fin_dates_id', 'fin_dates_name', 'start_date', 'end_date'),
    'PROJECT': ('proj_id', 'proj_short_name', 'clndr_id', 'last_recalc_date', 'plan_start_date', 'plan_end_date', 'scd_end_date'),
    'PROJWBS': ('wbs_id', 'proj_id', 'seq_num', 'proj_node_flag', 'status_code', 'wbs_short_name', 'wbs_name', 'parent_wbs_id'),
    'RSRC': ('rsrc_id', 'clndr_id', 'rsrc_name', 'rsrc_short_name', 'rsrc_title_name', 'rsrc_type'),
    'TASK': ('task_id', 'proj_id', 'wbs_id', 'clndr_id', 'phys_complete_pct', 'task_type', 'status_code', 'task_code', 'task_name', 'rsrc_id', 'total_float_hr_cnt', 'remain_drtn_hr_cnt', 'target_drtn_hr_cnt', 'cstr_date', 'act_start_date', 'act_end_date', 'late_start_date', 'late_end_date', 'early_start_date', 'early_end_date', 'restart_date', 'reend_date', 'target_start_date', 'target_end_date', 'rem_late_start_date', 'rem_late_end_date', 'cstr_type', 'suspend_date', 'resume_date', 'float_path', 'cstr_date2', 'cstr_type2', 'driving_path_flag'),
    'TASKPRED': ('task_pred_id', 'task_id', 'pred_task_id', 'proj_id', 'pred_proj_id', 'pred_type', 'lag_hr_cnt'),
    'TASKRSRC': ('taskrsrc_id', 'task_id', 'proj_id', 'rsrc_id', 'remain_qty', 'target_qty', 'act_ot_qty', 'act_reg_qty', 'target_cost', 'act_reg_cost', 'act_ot_cost', 'remain_cost', 'act_start_date', 'act_end_date', 'restart_date', 'reend_date', 'target_start_date', 'target_end_date', 'rem_late_start_date', 'rem_late_end_date', 'act_this_per_cost')
}

def parse_xer_file(xer_file: str) -> dict:
    """Parse xer into its varios tables"""
    tables = defaultdict(list)
    columns = list()
    curr_table = None

    for line in xer_file:
        row = line.rstrip("\n").split("\t")
        flag = row.pop(0)
        if flag == '%T':
            curr_table = row[0]
        elif flag == '%F':
            columns = row
        elif flag == '%R':
            if curr_table in DATA_TABLES:
                record = {
                    key: set_data_type(key, val)
                    for key, val in zip(columns, row)
                    if key in DATA_TABLES.get(curr_table, tuple())
                }

                tables[curr_table].append(record)

    return join_tables(tables)

def join_tables(tables: dict[str, list]) -> dict[str, list]:
    # project names are stored in the WBS table rather than the PROJECT table
    for proj in tables['PROJECT']:
        for node in tables['PROJWBS']:
            if node['proj_node_flag'] and node['proj_id'] == proj['proj_id']:
                proj['long_name'] = node['wbs_name']

    # join resource to each resource assignment
    for res_assign in tables['TASKRSRC']:
        for res in tables['RSRC']:
            if res_assign['rsrc_id'] == res['rsrc_id']:
                res_assign['rsrc_name'] = res['rsrc_name']
                break
    
    return tables

def set_data_type(key: str, val: str) -> Any:
    if not val:
        return
    if key.endswith(('_date', '_date2')):
        return datetime.strptime(val, '%Y-%m-%d %H:%M')
    if key.endswith('_num'):
        return int(val)
    if key.endswith(('_cnt', '_qty', '_cost')):
        return float(val)
    if key.endswith('_flag'):
        return val == 'Y'

    return val