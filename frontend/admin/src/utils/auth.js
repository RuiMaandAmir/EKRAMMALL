import Cookies from 'js-cookie';

const TokenKey = 'ekram_mall_admin_token';
const RefreshTokenKey = 'ekram_mall_admin_refresh_token';

export function getToken() {
  return Cookies.get(TokenKey);
}

export function setToken(token) {
  return Cookies.set(TokenKey, token);
}

export function removeToken() {
  return Cookies.remove(TokenKey);
}

export function getRefreshToken() {
  return Cookies.get(RefreshTokenKey);
}

export function setRefreshToken(token) {
  return Cookies.set(RefreshTokenKey, token);
}

export function removeRefreshToken() {
  return Cookies.remove(RefreshTokenKey);
}

export function clearAuth() {
  removeToken();
  removeRefreshToken();
  localStorage.removeItem('user');
} 