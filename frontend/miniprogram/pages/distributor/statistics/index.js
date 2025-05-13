const app = getApp()
const { request } = require('../../../utils/request')
const { formatNumber } = require('../../../utils/util')

Page({
  data: {
    currentDate: '',
    maxDate: '',
    totalCommission: '0.00',
    monthCommission: '0.00',
    totalOrders: 0,
    chartType: 'day',
    rankList: [],
    conversionRate: 0,
    averageOrderAmount: '0.00',
    averageCommissionRate: 0,
    activeUsers: 0,
    chartData: {
      xAxis: [],
      series: []
    }
  },

  onLoad() {
    // 设置日期范围
    const now = new Date()
    const maxDate = now.toISOString().split('T')[0]
    const currentDate = now.toISOString().split('T')[0].slice(0, 7)
    
    this.setData({
      currentDate,
      maxDate
    })

    // 加载数据
    this.loadStatistics()
    this.loadRankList()
    this.loadChartData()
  },

  // 日期变化
  onDateChange(e) {
    this.setData({
      currentDate: e.detail.value
    })
    this.loadStatistics()
    this.loadChartData()
  },

  // 切换图表类型
  switchChartType(e) {
    const type = e.currentTarget.dataset.type
    this.setData({
      chartType: type
    })
    this.loadChartData()
  },

  // 加载统计数据
  async loadStatistics() {
    try {
      const res = await request({
        url: '/distributor/statistics/',
        data: {
          date: this.data.currentDate
        }
      })

      this.setData({
        totalCommission: formatNumber(res.data.total_commission),
        monthCommission: formatNumber(res.data.month_commission),
        totalOrders: res.data.total_orders,
        conversionRate: res.data.conversion_rate,
        averageOrderAmount: formatNumber(res.data.average_order_amount),
        averageCommissionRate: res.data.average_commission_rate,
        activeUsers: res.data.active_users
      })
    } catch (error) {
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }
  },

  // 加载排行榜数据
  async loadRankList() {
    try {
      const res = await request({
        url: '/distributor/rank/',
        data: {
          date: this.data.currentDate
        }
      })

      this.setData({
        rankList: res.data.map(item => ({
          ...item,
          commission: formatNumber(item.commission)
        }))
      })
    } catch (error) {
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }
  },

  // 加载图表数据
  async loadChartData() {
    try {
      const res = await request({
        url: '/distributor/chart/',
        data: {
          date: this.data.currentDate,
          type: this.data.chartType
        }
      })

      this.setData({
        chartData: res.data
      })

      // 绘制图表
      this.drawChart()
    } catch (error) {
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }
  },

  // 绘制图表
  drawChart() {
    const ctx = wx.createCanvasContext('commissionChart')
    const { xAxis, series } = this.data.chartData
    const width = 650
    const height = 300
    const padding = 40
    const xAxisLength = width - padding * 2
    const yAxisLength = height - padding * 2
    const maxValue = Math.max(...series)

    // 绘制坐标轴
    ctx.setStrokeStyle('#ddd')
    ctx.setLineWidth(1)
    
    // X轴
    ctx.moveTo(padding, height - padding)
    ctx.lineTo(width - padding, height - padding)
    
    // Y轴
    ctx.moveTo(padding, padding)
    ctx.lineTo(padding, height - padding)
    
    ctx.stroke()

    // 绘制刻度
    ctx.setFontSize(10)
    ctx.setFillStyle('#999')
    
    // X轴刻度
    xAxis.forEach((item, index) => {
      const x = padding + (xAxisLength / (xAxis.length - 1)) * index
      ctx.fillText(item, x - 10, height - padding + 15)
    })

    // Y轴刻度
    const yStep = maxValue / 5
    for (let i = 0; i <= 5; i++) {
      const y = height - padding - (yAxisLength / 5) * i
      const value = (yStep * i).toFixed(2)
      ctx.fillText(value, padding - 30, y + 5)
    }

    // 绘制折线
    ctx.setStrokeStyle('#ff4d4f')
    ctx.setLineWidth(2)
    ctx.beginPath()

    series.forEach((value, index) => {
      const x = padding + (xAxisLength / (series.length - 1)) * index
      const y = height - padding - (value / maxValue) * yAxisLength
      
      if (index === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })

    ctx.stroke()

    // 绘制数据点
    ctx.setFillStyle('#ff4d4f')
    series.forEach((value, index) => {
      const x = padding + (xAxisLength / (series.length - 1)) * index
      const y = height - padding - (value / maxValue) * yAxisLength
      ctx.beginPath()
      ctx.arc(x, y, 4, 0, 2 * Math.PI)
      ctx.fill()
    })

    ctx.draw()
  }
}) 