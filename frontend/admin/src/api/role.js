import request from '@/utils/request';

/**
 * 获取角色列表
 * @param {Object} params - 查询参数
 * @returns {Promise} - 返回角色列表数据
 */
export function getRoleList(params) {
  return request({
    url: '/roles',
    method: 'get',
    params
  });
}

/**
 * 创建角色
 * @param {Object} data - 角色数据
 * @returns {Promise} - 返回创建结果
 */
export function createRole(data) {
  return request({
    url: '/roles',
    method: 'post',
    data
  });
}

/**
 * 更新角色
 * @param {number|string} id - 角色ID
 * @param {Object} data - 角色更新数据
 * @returns {Promise} - 返回更新结果
 */
export function updateRole(id, data) {
  return request({
    url: `/roles/${id}`,
    method: 'put',
    data
  });
}

/**
 * 删除角色
 * @param {number|string} id - 角色ID
 * @returns {Promise} - 返回删除结果
 */
export function deleteRole(id) {
  return request({
    url: `/roles/${id}`,
    method: 'delete'
  });
}

/**
 * 获取角色详情
 * @param {number|string} id - 角色ID
 * @returns {Promise} - 返回角色详情
 */
export function getRoleDetail(id) {
  return request({
    url: `/roles/${id}`,
    method: 'get'
  });
}

/**
 * 获取角色权限
 * @param {number|string} id - 角色ID
 * @returns {Promise} - 返回角色权限
 */
export function getRolePermissions(id) {
  return request({
    url: `/roles/${id}/permissions`,
    method: 'get'
  });
}

/**
 * 更新角色权限
 * @param {number|string} id - 角色ID
 * @param {Array} permissionIds - 权限ID数组
 * @returns {Promise} - 返回更新结果
 */
export function updateRolePermissions(id, permissionIds) {
  return request({
    url: `/roles/${id}/permissions`,
    method: 'put',
    data: { permissionIds }
  });
}

/**
 * 批量删除角色
 * @param {Array} ids - 角色ID数组
 * @returns {Promise} - 返回批量删除结果
 */
export function batchDeleteRoles(ids) {
  return request({
    url: '/roles/batch',
    method: 'delete',
    data: { ids }
  });
}

/**
 * 导出角色数据
 * @returns {Promise} - 返回导出结果
 */
export function exportRoles() {
  return request({
    url: '/roles/export',
    method: 'get',
    responseType: 'blob'
  });
}

/**
 * 获取所有角色（用于下拉选择）
 * @returns {Promise} - 返回所有角色
 */
export function getAllRoles() {
  return request({
    url: '/roles/all',
    method: 'get'
  });
}

/**
 * 获取角色下的用户列表
 * @param {number|string} id - 角色ID
 * @param {Object} params - 查询参数
 * @returns {Promise} 返回请求的Promise对象
 */
export function getRoleUsers(id, params) {
  return request({
    url: `/api/roles/${id}/users`,
    method: 'get',
    params
  });
}

/**
 * 获取权限树
 * @returns {Promise} 返回请求的Promise对象
 */
export function getPermissionTree() {
  return request({
    url: '/api/permissions/tree',
    method: 'get'
  });
}

/**
 * 获取当前用户的权限列表
 * @returns {Promise} 返回请求的Promise对象
 */
export function getUserPermissions() {
  return request({
    url: '/api/user/permissions',
    method: 'get'
  });
}

/**
 * 获取指定用户的角色列表
 * @param {number|string} userId - 用户ID
 * @returns {Promise} 返回请求的Promise对象
 */
export function getUserRoles(userId) {
  return request({
    url: `/api/users/${userId}/roles`,
    method: 'get'
  });
}

/**
 * 设置用户角色
 * @param {number|string} userId - 用户ID
 * @param {Array} roleIds - 角色ID数组
 * @returns {Promise} 返回请求的Promise对象
 */
export function setUserRoles(userId, roleIds) {
  return request({
    url: `/api/users/${userId}/roles`,
    method: 'put',
    data: { role_ids: roleIds }
  });
} 