/**
 * 样品流转相关API
 */

import { get, post } from './request'

// 流转管理
export const getWorkflowList = (params) => get('/workflow/', params)
export const getWorkflow = (id) => get(`/workflow/${id}/`)
export const transitionWorkflow = (id, data) => post(`/workflow/${id}/transition/`, data)
export const assignWorkflow = (id, data) => post(`/workflow/${id}/assign/`, data)
export const getMyTasks = () => get('/workflow/my_tasks/')
export const getStatusOptions = () => get('/workflow/status_options/')

// 流转日志
export const getWorkflowLogs = (params) => get('/workflow/logs/', params)

// 试验任务
export const getTaskList = (params) => get('/workflow/tasks/', params)
export const createTask = (data) => post('/workflow/tasks/', data)
export const startTask = (id) => post(`/workflow/tasks/${id}/start/`)
export const completeTask = (id) => post(`/workflow/tasks/${id}/complete/`)
