<template>
  <div class="statistics-container">
    <!-- 时间范围选择 -->
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>数据统计</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="exportData">导出数据</el-button>
      </div>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="yyyy-MM-dd"
            @change="handleDateChange">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="活动">
          <el-select v-model="searchForm.activity" placeholder="请选择活动" clearable>
            <el-option
              v-for="item in activityOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="商品">
          <el-select v-model="searchForm.product" placeholder="请选择商品" clearable>
            <el-option
              v-for="item in productOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据概览 -->
    <el-row :gutter="20" class="overview-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="overview-item">
            <div class="overview-title">总销售额</div>
            <div class="overview-value">¥{{ overview.total_sales }}</div>
            <div class="overview-trend" :class="overview.sales_trend >= 0 ? 'up' : 'down'">
              {{ overview.sales_trend >= 0 ? '+' : '' }}{{ overview.sales_trend }}%
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="overview-item">
            <div class="overview-title">总订单数</div>
            <div class="overview-value">{{ overview.total_orders }}</div>
            <div class="overview-trend" :class="overview.orders_trend >= 0 ? 'up' : 'down'">
              {{ overview.orders_trend >= 0 ? '+' : '' }}{{ overview.orders_trend }}%
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="overview-item">
            <div class="overview-title">优惠券使用</div>
            <div class="overview-value">{{ overview.coupon_used }}</div>
            <div class="overview-trend" :class="overview.coupon_trend >= 0 ? 'up' : 'down'">
              {{ overview.coupon_trend >= 0 ? '+' : '' }}{{ overview.coupon_trend }}%
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="overview-item">
            <div class="overview-title">活动参与</div>
            <div class="overview-value">{{ overview.activity_participants }}</div>
            <div class="overview-trend" :class="overview.participants_trend >= 0 ? 'up' : 'down'">
              {{ overview.participants_trend >= 0 ? '+' : '' }}{{ overview.participants_trend }}%
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表展示 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <div slot="header">
            <span>销售趋势</span>
            <el-radio-group v-model="salesChartType" size="small" style="float: right">
              <el-radio-button label="day">日</el-radio-button>
              <el-radio-button label="week">周</el-radio-button>
              <el-radio-button label="month">月</el-radio-button>
            </el-radio-group>
          </div>
          <div class="chart-container">
            <v-chart :options="salesChart" autoresize></v-chart>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <div slot="header">
            <span>优惠券使用情况</span>
          </div>
          <div class="chart-container">
            <v-chart :options="couponChart" autoresize></v-chart>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <div slot="header">
            <span>活动效果分析</span>
          </div>
          <div class="chart-container">
            <v-chart :options="activityChart" autoresize></v-chart>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <div slot="header">
            <span>商品销售排行</span>
          </div>
          <div class="chart-container">
            <v-chart :options="productChart" autoresize></v-chart>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 数据表格 -->
    <el-card class="box-card">
      <div slot="header">
        <span>详细数据</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="exportDetailData">导出详细数据</el-button>
      </div>
      <el-table :data="detailData" style="width: 100%" v-loading="loading">
        <el-table-column prop="date" label="日期" width="180"></el-table-column>
        <el-table-column prop="activity_name" label="活动名称" width="180"></el-table-column>
        <el-table-column prop="product_name" label="商品名称" width="180"></el-table-column>
        <el-table-column prop="sales" label="销售额" width="120">
          <template slot-scope="scope">
            ¥{{ scope.row.sales }}
          </template>
        </el-table-column>
        <el-table-column prop="orders" label="订单数" width="120"></el-table-column>
        <el-table-column prop="coupon_used" label="优惠券使用" width="120"></el-table-column>
        <el-table-column prop="conversion_rate" label="转化率" width="120">
          <template slot-scope="scope">
            {{ scope.row.conversion_rate }}%
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { getPromotionStats, getCouponStats, getActivityStats } from '@/api/promotion'
import ECharts from 'vue-echarts'
import 'echarts/lib/chart/line'
import 'echarts/lib/chart/bar'
import 'echarts/lib/chart/pie'
import 'echarts/lib/component/tooltip'
import 'echarts/lib/component/title'
import 'echarts/lib/component/legend'
import 'echarts/lib/component/grid'

export default {
  name: 'Statistics',
  components: {
    'v-chart': ECharts
  },
  data() {
    return {
      searchForm: {
        dateRange: [],
        activity: '',
        product: ''
      },
      activityOptions: [],
      productOptions: [],
      overview: {
        total_sales: 0,
        total_orders: 0,
        coupon_used: 0,
        activity_participants: 0,
        sales_trend: 0,
        orders_trend: 0,
        coupon_trend: 0,
        participants_trend: 0
      },
      salesChartType: 'day',
      salesChart: {
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: []
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          data: [],
          type: 'line',
          smooth: true
        }]
      },
      couponChart: {
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        series: [{
          type: 'pie',
          radius: '50%',
          data: [],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      },
      activityChart: {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['销售额', '订单数', '转化率']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: []
        },
        yAxis: [
          {
            type: 'value',
            name: '金额/数量'
          },
          {
            type: 'value',
            name: '转化率',
            min: 0,
            max: 100,
            interval: 20,
            axisLabel: {
              formatter: '{value}%'
            }
          }
        ],
        series: [
          {
            name: '销售额',
            type: 'bar',
            data: []
          },
          {
            name: '订单数',
            type: 'bar',
            data: []
          },
          {
            name: '转化率',
            type: 'line',
            yAxisIndex: 1,
            data: []
          }
        ]
      },
      productChart: {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'value'
        },
        yAxis: {
          type: 'category',
          data: []
        },
        series: [{
          type: 'bar',
          data: []
        }]
      },
      detailData: [],
      loading: false
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const params = {
          start_date: this.searchForm.dateRange[0],
          end_date: this.searchForm.dateRange[1],
          activity: this.searchForm.activity,
          product: this.searchForm.product
        }

        const [promotionStats, couponStats, activityStats] = await Promise.all([
          getPromotionStats(params),
          getCouponStats(params),
          getActivityStats(params)
        ])

        this.updateOverview(promotionStats.data)
        this.updateCharts(couponStats.data, activityStats.data)
        this.updateDetailData(promotionStats.data)
      } catch (error) {
        this.$message.error('获取数据失败')
      } finally {
        this.loading = false
      }
    },
    updateOverview(data) {
      this.overview = {
        total_sales: data.total_sales || 0,
        total_orders: data.total_orders || 0,
        coupon_used: data.coupon_used || 0,
        activity_participants: data.activity_participants || 0,
        sales_trend: data.sales_trend || 0,
        orders_trend: data.orders_trend || 0,
        coupon_trend: data.coupon_trend || 0,
        participants_trend: data.participants_trend || 0
      }
    },
    updateCharts(couponData, activityData) {
      // 更新销售趋势图
      this.salesChart.xAxis.data = activityData.sales_trend.map(item => item.date)
      this.salesChart.series[0].data = activityData.sales_trend.map(item => item.sales)

      // 更新优惠券使用图
      this.couponChart.series[0].data = couponData.type_stats.map(item => ({
        name: item.discount_type === 'fixed' ? '固定金额' : '百分比',
        value: item.count
      }))

      // 更新活动效果图
      this.activityChart.xAxis.data = activityData.activity_stats.map(item => item.name)
      this.activityChart.series[0].data = activityData.activity_stats.map(item => item.total_revenue)
      this.activityChart.series[1].data = activityData.activity_stats.map(item => item.total_sold)
      this.activityChart.series[2].data = activityData.activity_stats.map(item => item.conversion_rate)

      // 更新商品销售排行图
      this.productChart.yAxis.data = activityData.product_ranking.map(item => item.product__name)
      this.productChart.series[0].data = activityData.product_ranking.map(item => item.sold_count)
    },
    updateDetailData(data) {
      this.detailData = data.detail_data || []
    },
    handleDateChange() {
      this.fetchData()
    },
    handleSearch() {
      this.fetchData()
    },
    resetSearch() {
      this.searchForm = {
        dateRange: [],
        activity: '',
        product: ''
      }
      this.fetchData()
    },
    exportData() {
      // 实现数据导出功能
      const params = {
        start_date: this.searchForm.dateRange[0],
        end_date: this.searchForm.dateRange[1],
        activity: this.searchForm.activity,
        product: this.searchForm.product
      }
      window.location.href = `/api/export-promotion-stats/?${new URLSearchParams(params).toString()}`
    },
    exportDetailData() {
      // 实现详细数据导出功能
      const params = {
        start_date: this.searchForm.dateRange[0],
        end_date: this.searchForm.dateRange[1],
        activity: this.searchForm.activity,
        product: this.searchForm.product,
        type: 'detail'
      }
      window.location.href = `/api/export-promotion-stats/?${new URLSearchParams(params).toString()}`
    }
  }
}
</script>

<style scoped>
.statistics-container {
  padding: 20px;
}
.search-form {
  margin-bottom: 20px;
}
.overview-row {
  margin-bottom: 20px;
}
.overview-item {
  text-align: center;
  padding: 20px 0;
}
.overview-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}
.overview-value {
  font-size: 24px;
  color: #303133;
  margin-bottom: 10px;
}
.overview-trend {
  font-size: 12px;
}
.overview-trend.up {
  color: #67C23A;
}
.overview-trend.down {
  color: #F56C6C;
}
.chart-row {
  margin-bottom: 20px;
}
.chart-container {
  height: 400px;
}
</style> 