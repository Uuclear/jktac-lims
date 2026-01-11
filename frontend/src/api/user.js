/**
 * 用户相关API
 */

import { get, post, put, del } from './request'

// 登录
export const login = (data) => post('/users/auth/login/', data)

// 登出
export const logout = (data) => post('/users/auth/logout/', data)

// 注册
export const register = (data) => post('/users/auth/register/', data)

// 获取当前用户信息
export const getUserInfo = () => get('/users/me/')

// 更新当前用户信息
export const updateUserInfo = (data) => put('/users/me/', data)

// 修改密码
export const changePassword = (data) => post('/users/change_password/', data)

// 用户管理
export const getUserList = (params) => get('/users/', params)
export const createUser = (data) => post('/users/', data)
export const updateUser = (id, data) => put(`/users/${id}/`, data)
export const deleteUser = (id) => del(`/users/${id}/`)
export const resetUserPassword = (id, data) => post(`/users/${id}/reset_password/`, data)

// 部门管理
export const getDepartmentList = (params) => get('/users/departments/', params)
export const getDepartmentTree = () => get('/users/departments/tree/')
export const createDepartment = (data) => post('/users/departments/', data)
export const updateDepartment = (id, data) => put(`/users/departments/${id}/`, data)
export const deleteDepartment = (id) => del(`/users/departments/${id}/`)
