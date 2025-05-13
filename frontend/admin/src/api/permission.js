import request from '@/utils/request';

/**
 * 获取权限列表
 * @param {Object} params - 查询参数
 * @returns {Promise} - 返回权限列表数据
 */
export function getPermissionList(params) {
  return request({
    url: '/permissions',
    method: 'get',
    params
  });
}

/**
 * 获取权限树形结构
 * @returns {Promise} - 返回权限树形结构数据
 */
export function getPermissionTree() {
  return request({
    url: '/permissions/tree',
    method: 'get'
  });
}

/**
 * 创建权限
 * @param {Object} data - 权限数据
 * @returns {Promise} - 返回创建结果
 */
export function createPermission(data) {
  return request({
    url: '/permissions',
    method: 'post',
    data
  });
}

/**
 * 更新权限
 * @param {number|string} id - 权限ID
 * @param {Object} data - 权限更新数据
 * @returns {Promise} - 返回更新结果
 */
export function updatePermission(id, data) {
  return request({
    url: `/permissions/${id}`,
    method: 'put',
    data
  });
}

/**
 * 删除权限
 * @param {number|string} id - 权限ID
 * @returns {Promise} - 返回删除结果
 */
export function deletePermission(id) {
  return request({
    url: `/permissions/${id}`,
    method: 'delete'
  });
}

/**
 * 获取权限详情
 * @param {number|string} id - 权限ID
 * @returns {Promise} - 返回权限详情
 */
export function getPermissionDetail(id) {
  return request({
    url: `/permissions/${id}`,
    method: 'get'
  });
}

/**
 * 批量删除权限
 * @param {Array} ids - 权限ID数组
 * @returns {Promise} - 返回批量删除结果
 */
export function batchDeletePermissions(ids) {
  return request({
    url: '/permissions/batch',
    method: 'delete',
    data: { ids }
  });
}

/**
 * 批量创建权限
 * @param {Array} data - 权限数据数组
 * @returns {Promise} 返回请求的Promise对象
 */
export function batchCreatePermissions(data) {
  return request({
    url: '/permissions/batch',
    method: 'post',
    data
  });
}

/**
 * 导出权限数据
 * @returns {Promise} - 返回导出结果
 */
export function exportPermissions() {
  return request({
    url: '/permissions/export',
    method: 'get',
    responseType: 'blob'
  });
}

/**
 * 导入权限数据
 * @param {Object} data - 权限导入数据
 * @returns {Promise} 返回请求的Promise对象
 */
export function importPermissions(data) {
  return request({
    url: '/permissions/import',
    method: 'post',
    data
  });
}

/**
 * 同步权限数据（从路由配置中）
 * @returns {Promise} 返回请求的Promise对象
 */
export function syncPermissions() {
  return request({
    url: '/permissions/sync',
    method: 'post'
  });
}

/**
 * 分配权限给角色
 * @param {number|string} roleId - 角色ID
 * @param {Array} permissionIds - 权限ID数组
 * @returns {Promise} 返回请求的Promise对象
 */
export function assignPermissionsToRole(roleId, permissionIds) {
  return request({
    url: `/roles/${roleId}/permissions`,
    method: 'put',
    data: { permissionIds }
  });
}

/**
 * 获取角色的权限ID列表
 * @param {number|string} roleId - 角色ID
 * @returns {Promise} 返回请求的Promise对象
 */
export function getRolePermissionIds(roleId) {
  return request({
    url: `/roles/${roleId}/permissions`,
    method: 'get'
  });
} 