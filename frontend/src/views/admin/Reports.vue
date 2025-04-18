<template>
  <div class="reports-container">
    <h1>Analytics Dashboard</h1>
    
    <div class="filter-controls">
      <div class="date-range">
        <label>Date Range:</label>
        <select v-model="selectedDateRange" class="form-control">
          <option value="today">Today</option>
          <option value="week">Last 7 Days</option>
          <option value="month">Last 30 Days</option>
          <option value="quarter">Last 90 Days</option>
          <option value="year">Last 365 Days</option>
        </select>
      </div>
      
      <button @click="generateReports" class="btn btn-primary">
        <i class="fas fa-sync"></i> Update Reports
      </button>
    </div>
    
    <div class="report-grid">
      <!-- KPI Cards -->
      <div class="kpi-cards">
        <div class="kpi-card">
          <div class="kpi-icon bg-primary">
            <i class="fas fa-users"></i>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">{{ metrics.totalCustomers }}</div>
            <div class="kpi-label">Total Customers</div>
            <div class="kpi-trend" :class="metrics.customerGrowth >= 0 ? 'positive' : 'negative'">
              <i :class="metrics.customerGrowth >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
              {{ Math.abs(metrics.customerGrowth) }}% from previous period
            </div>
          </div>
        </div>
        
        <div class="kpi-card">
          <div class="kpi-icon bg-success">
            <i class="fas fa-briefcase"></i>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">{{ metrics.totalProfessionals }}</div>
            <div class="kpi-label">Total Professionals</div>
            <div class="kpi-trend" :class="metrics.professionalGrowth >= 0 ? 'positive' : 'negative'">
              <i :class="metrics.professionalGrowth >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
              {{ Math.abs(metrics.professionalGrowth) }}% from previous period
            </div>
          </div>
        </div>
        
        <div class="kpi-card">
          <div class="kpi-icon bg-info">
            <i class="fas fa-calendar-check"></i>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">{{ metrics.serviceRequests }}</div>
            <div class="kpi-label">Service Requests</div>
            <div class="kpi-trend" :class="metrics.requestGrowth >= 0 ? 'positive' : 'negative'">
              <i :class="metrics.requestGrowth >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
              {{ Math.abs(metrics.requestGrowth) }}% from previous period
            </div>
          </div>
        </div>
        
        <div class="kpi-card">
          <div class="kpi-icon bg-warning">
            <i class="fas fa-money-bill-wave"></i>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">${{ formatMoney(metrics.revenue) }}</div>
            <div class="kpi-label">Total Revenue</div>
            <div class="kpi-trend" :class="metrics.revenueGrowth >= 0 ? 'positive' : 'negative'">
              <i :class="metrics.revenueGrowth >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
              {{ Math.abs(metrics.revenueGrowth) }}% from previous period
            </div>
          </div>
        </div>
      </div>
      
 
    </div>
    
    <div class="report-table-section">
      <h2>Top Performing Services</h2>
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Service</th>
            <th>Category</th>
            <th>Requests</th>
            <th>Revenue</th>
            <th>Avg. Rating</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(service, index) in topServices" :key="index">
            <td>{{ service.name }}</td>
            <td>{{ service.category }}</td>
            <td>{{ service.requests }}</td>
            <td>${{ formatMoney(service.revenue) }}</td>
            <td>
              <div class="rating">
                <i class="fas fa-star"></i> {{ service.rating }}
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div class="report-actions">
      <button @click="exportPDF" class="btn btn-secondary">
        <i class="fas fa-file-pdf"></i> Export as PDF
      </button>
      <button @click="exportCSV" class="btn btn-secondary">
        <i class="fas fa-file-csv"></i> Export as CSV
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminReports',
  data() {
    return {
      selectedDateRange: 'month',
      metrics: {
        totalCustomers: 0,
        customerGrowth: 0,
        totalProfessionals: 0,
        professionalGrowth: 0,
        serviceRequests: 0,
        requestGrowth: 0,
        revenue: 0,
        revenueGrowth: 0
      },
      topServices: [],
      charts: {
        revenue: null,
        category: null,
        satisfaction: null,
        professional: null
      }
    }
  },
  mounted() {
    this.generateReports()
  },
  methods: {
    async generateReports() {
      // In a real application, fetch data from API based on selectedDateRange
      // For demonstration, generate mock data
      this.generateMockData()
      
      // Initialize or update charts
      this.$nextTick(() => {
        this.initCharts()
      })
    },
    
    generateMockData() {
      // Generate random metrics with realistic values
      this.metrics = {
        totalCustomers: Math.floor(Math.random() * 1000) + 500,
        customerGrowth: Math.floor(Math.random() * 30) - 10,
        totalProfessionals: Math.floor(Math.random() * 200) + 100,
        professionalGrowth: Math.floor(Math.random() * 20) + 5,
        serviceRequests: Math.floor(Math.random() * 2000) + 1000,
        requestGrowth: Math.floor(Math.random() * 40) - 5,
        revenue: Math.floor(Math.random() * 100000) + 50000,
        revenueGrowth: Math.floor(Math.random() * 25) + 5
      }
      
      // Generate top services data
      this.topServices = [
        {
          name: 'Plumbing Repair',
          category: 'Plumbing',
          requests: Math.floor(Math.random() * 200) + 100,
          revenue: Math.floor(Math.random() * 10000) + 5000,
          rating: (Math.random() * 2 + 3).toFixed(1)
        },
        {
          name: 'Electrical Installation',
          category: 'Electrical',
          requests: Math.floor(Math.random() * 150) + 100,
          revenue: Math.floor(Math.random() * 15000) + 7000,
          rating: (Math.random() * 2 + 3).toFixed(1)
        },
        {
          name: 'House Cleaning',
          category: 'Cleaning',
          requests: Math.floor(Math.random() * 300) + 200,
          revenue: Math.floor(Math.random() * 8000) + 3000,
          rating: (Math.random() * 2 + 3).toFixed(1)
        },
        {
          name: 'Lawn Mowing',
          category: 'Landscaping',
          requests: Math.floor(Math.random() * 150) + 80,
          revenue: Math.floor(Math.random() * 6000) + 2000,
          rating: (Math.random() * 2 + 3).toFixed(1)
        },
        {
          name: 'Interior Painting',
          category: 'Home Improvement',
          requests: Math.floor(Math.random() * 100) + 50,
          revenue: Math.floor(Math.random() * 12000) + 6000,
          rating: (Math.random() * 2 + 3).toFixed(1)
        }
      ]
    },
    
   
    
    formatMoney(value) {
      return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")
    },
    
    exportPDF() {
      alert('PDF export functionality would be implemented here')
    },
    
    exportCSV() {
      alert('CSV export functionality would be implemented here')
    }
  }
}
</script>

<style scoped>
.reports-container {
  padding: 1.5rem;
}

h1, h2, h3 {
  color: #333;
  margin-bottom: 1.5rem;
}

.filter-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-range select {
  width: 150px;
}

/* KPI Cards */
.kpi-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.kpi-card {
  display: flex;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.kpi-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  font-size: 2rem;
  color: white;
}

.bg-primary {
  background-color: #007bff;
}

.bg-success {
  background-color: #28a745;
}

.bg-info {
  background-color: #17a2b8;
}

.bg-warning {
  background-color: #ffc107;
}

.kpi-content {
  flex: 1;
  padding: 1rem;
}

.kpi-value {
  font-size: 1.8rem;
  font-weight: 600;
}

.kpi-label {
  color: #666;
  margin-bottom: 0.5rem;
}

.kpi-trend {
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.kpi-trend.positive {
  color: #28a745;
}

.kpi-trend.negative {
  color: #dc3545;
}

/* Charts */
.chart-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-container {
  background-color: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.chart-container h3 {
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

canvas {
  width: 100%;
  height: 250px;
  background-color: #fafafa;
  border-radius: 4px;
}

/* Tables */
.report-table-section {
  margin-bottom: 2rem;
}

.table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  border-radius: 8px;
  overflow: hidden;
}

.table th {
  background-color: #f8f9fa;
  padding: 1rem;
  text-align: left;
}

.table td {
  padding: 1rem;
  border-top: 1px solid #eee;
}

.rating {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.fa-star {
  color: #ffc107;
}

/* Report Actions */
.report-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .chart-row {
    grid-template-columns: 1fr;
  }
  
  .filter-controls {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .report-actions {
    flex-direction: column;
  }
  
  .report-actions button {
    width: 100%;
  }
}
</style> 