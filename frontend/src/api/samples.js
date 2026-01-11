/**
 * 委托收样相关API
 */

import { get, post, put, del } from './request'

// 委托方管理
export const getClientList = (params) => get('/samples/clients/', params)
export const getClient = (id) => get(`/samples/clients/${id}/`)
export const createClient = (data) => post('/samples/clients/', data)
export const updateClient = (id, data) => put(`/samples/clients/${id}/`, data)
export const deleteClient = (id) => del(`/samples/clients/${id}/`)

// 委托单管理
export const getCommissionList = (params) => get('/samples/commissions/', params)
export const getCommission = (id) => get(`/samples/commissions/${id}/`)
export const createCommission = (data) => post('/samples/commissions/', data)
export const updateCommission = (id, data) => put(`/samples/commissions/${id}/`, data)
export const deleteCommission = (id) => del(`/samples/commissions/${id}/`)
export const submitCommission = (id) => post(`/samples/commissions/${id}/submit/`)
export const cancelCommission = (id) => post(`/samples/commissions/${id}/cancel/`)

// 收样记录管理
export const getReceiveList = (params) => get('/samples/receives/', params)
export const getReceive = (id) => get(`/samples/receives/${id}/`)
export const createReceive = (data) => post('/samples/receives/', data)
