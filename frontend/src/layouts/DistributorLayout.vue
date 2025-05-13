<template>
  <div class="distributor-layout">
    <el-container>
      <el-aside width="200px">
        <el-menu
          :default-active="activeMenu"
          class="distributor-menu"
          router
        >
          <el-menu-item index="/distributor/dashboard">
            <i class="el-icon-s-home"></i>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/distributor/links">
            <i class="el-icon-share"></i>
            <span>分销链接</span>
          </el-menu-item>
          <el-menu-item index="/distributor/commissions">
            <i class="el-icon-money"></i>
            <span>佣金管理</span>
          </el-menu-item>
          <el-menu-item index="/distributor/team">
            <i class="el-icon-user"></i>
            <span>团队管理</span>
          </el-menu-item>
          <el-menu-item index="/distributor/profile">
            <i class="el-icon-s-custom"></i>
            <span>个人中心</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header>
          <div class="header-content">
            <h2>分销商中心</h2>
            <el-dropdown>
              <span class="el-dropdown-link">
                {{ userInfo.username }}<i class="el-icon-arrow-down el-icon--right"></i>
              </span>
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item @click.native="goToProfile">个人中心</el-dropdown-item>
                <el-dropdown-item @click.native="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
          </div>
        </el-header>
        <el-main>
          <router-view></router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'DistributorLayout',
  computed: {
    ...mapState({
      userInfo: state => state.user.userInfo
    }),
    activeMenu() {
      return this.$route.path
    }
  },
  methods: {
    goToProfile() {
      this.$router.push('/distributor/profile')
    },
    async logout() {
      try {
        await this.$store.dispatch('user/logout')
        this.$router.push('/login')
        this.$message.success('退出成功')
      } catch (error) {
        this.$message.error(error.message || '退出失败')
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.distributor-layout {
  height: 100vh;
  
  .el-aside {
    background-color: #304156;
    
    .distributor-menu {
      border-right: none;
    }
  }
  
  .el-header {
    background-color: #fff;
    border-bottom: 1px solid #e6e6e6;
    
    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      height: 100%;
      
      h2 {
        margin: 0;
        font-size: 18px;
        color: #303133;
      }
      
      .el-dropdown-link {
        cursor: pointer;
        color: #409EFF;
      }
    }
  }
  
  .el-main {
    background-color: #f0f2f5;
    padding: 20px;
  }
}
</style> 