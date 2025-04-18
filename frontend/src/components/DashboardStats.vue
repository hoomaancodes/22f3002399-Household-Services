<template>
  <div class="dashboard-stats">
    <div class="row">
      <div v-for="(stat, index) in stats" :key="index" class="col-md-3 col-sm-6 mb-4">
        <div class="card h-100">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="stat-icon me-3" :class="stat.colorClass">
                <i :class="stat.icon"></i>
              </div>
              <div>
                <h6 class="stat-title mb-1">{{ stat.title }}</h6>
                <h3 class="stat-value mb-0">{{ stat.value }}</h3>
              </div>
            </div>
            <div class="stat-trend mt-3" v-if="stat.trend">
              <i class="fas" :class="stat.trend.direction === 'up' ? 'fa-arrow-up text-success' : 'fa-arrow-down text-danger'"></i>
              <span>{{ stat.trend.value }}% since last month</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showCharts" class="row mt-4">
      <div class="col-md-6 mb-4">
        <div class="card h-100">
          <div class="card-header">
            <h6 class="mb-0">{{ chartData.areaChart.title }}</h6>
          </div>
          <div class="card-body d-flex align-items-center justify-content-center">
            <div class="area-chart-placeholder">
              <!-- Area chart would be rendered here using chart.js or other library -->
              <div v-if="isLoading" class="text-center">
                <div class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <div v-else class="chart-image">
                <div class="chart-circle" style="background-color: #4e73df; width: 60%; height: 60%;"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-md-6 mb-4">
        <div class="card h-100">
          <div class="card-header">
            <h6 class="mb-0">{{ chartData.barChart.title }}</h6>
          </div>
          <div class="card-body d-flex align-items-center justify-content-center">
            <div class="bar-chart-placeholder">
              <!-- Bar chart would be rendered here using chart.js or other library -->
              <div v-if="isLoading" class="text-center">
                <div class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <div v-else class="chart-bars d-flex align-items-end">
                <div v-for="(bar, i) in [70, 45, 60, 35, 50]" :key="i" 
                  class="chart-bar" 
                  :style="{height: bar + '%', backgroundColor: getBarColor(i)}">
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardStats',
  props: {
    userRole: {
      type: String,
      required: true,
      validator: value => ['admin', 'professional', 'customer'].includes(value)
    },
    showCharts: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      isLoading: false,
      adminStats: [
        {
          title: 'Total Services',
          value: 24,
          icon: 'fas fa-toolbox',
          colorClass: 'bg-primary',
          trend: { direction: 'up', value: 12 }
        },
        {
          title: 'Professionals',
          value: 42,
          icon: 'fas fa-user-tie',
          colorClass: 'bg-success',
          trend: { direction: 'up', value: 8 }
        },
        {
          title: 'Customers',
          value: 215,
          icon: 'fas fa-users',
          colorClass: 'bg-info',
          trend: { direction: 'up', value: 15 }
        },
        {
          title: 'Pending Approvals',
          value: 6,
          icon: 'fas fa-clock',
          colorClass: 'bg-warning'
        }
      ],
      professionalStats: [
        {
          title: 'New Requests',
          value: 8,
          icon: 'fas fa-bell',
          colorClass: 'bg-primary'
        },
        {
          title: 'Active Jobs',
          value: 3,
          icon: 'fas fa-briefcase',
          colorClass: 'bg-info'
        },
        {
          title: 'Completed Jobs',
          value: 47,
          icon: 'fas fa-check-circle',
          colorClass: 'bg-success',
          trend: { direction: 'up', value: 12 }
        },
        {
          title: 'Earnings',
          value: '$2,150',
          icon: 'fas fa-dollar-sign',
          colorClass: 'bg-warning',
          trend: { direction: 'up', value: 8 }
        }
      ],
      customerStats: [
        {
          title: 'Active Requests',
          value: 2,
          icon: 'fas fa-spinner',
          colorClass: 'bg-primary'
        },
        {
          title: 'Completed Services',
          value: 15,
          icon: 'fas fa-check-circle',
          colorClass: 'bg-success'
        },
        {
          title: 'Total Spent',
          value: '$750',
          icon: 'fas fa-dollar-sign',
          colorClass: 'bg-info'
        },
        {
          title: 'Saved Services',
          value: 5,
          icon: 'fas fa-bookmark',
          colorClass: 'bg-warning'
        }
      ],
      chartData: {
        areaChart: {
          title: 'Service Usage Distribution'
        },
        barChart: {
          title: 'Monthly Statistics'
        }
      }
    };
  },
  computed: {
    stats() {
      switch(this.userRole) {
        case 'admin':
          return this.adminStats;
        case 'professional':
          return this.professionalStats;
        case 'customer':
          return this.customerStats;
        default:
          return [];
      }
    }
  },
  methods: {
    fetchStats() {
      // This would fetch real stats from the API
      this.isLoading = true;
      setTimeout(() => {
        this.isLoading = false;
      }, 800);
    },
    getBarColor(index) {
      const colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b'];
      return colors[index % colors.length];
    }
  },
  created() {
    this.fetchStats();
  }
}
</script>

<style scoped>
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}
.bg-primary {
  background-color: #4e73df;
}
.bg-success {
  background-color: #1cc88a;
}
.bg-info {
  background-color: #36b9cc;
}
.bg-warning {
  background-color: #f6c23e;
}
.stat-trend {
  font-size: 0.8rem;
  color: #858796;
}
.area-chart-placeholder, .bar-chart-placeholder {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.chart-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.chart-circle {
  border-radius: 50%;
}
.chart-bars {
  width: 100%;
  height: 100%;
  justify-content: space-around;
}
.chart-bar {
  width: 12%;
  margin: 0 2%;
  border-radius: 4px 4px 0 0;
}
</style> 