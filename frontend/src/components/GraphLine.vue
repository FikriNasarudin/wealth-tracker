<template>
  <div style="position: relative; width: 100%; height: 300px;">
    <Line :data="chartData" :options="mergedOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, Filler } from 'chart.js'
import { Line } from 'vue-chartjs'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const props = defineProps({
  labels: {
    type: Array,
    required: true
  },
  datasets: {
    type: Array,
    required: true
  },
  options: {
    type: Object,
    default: () => ({})
  }
})

const chartData = computed(() => {
  return {
    labels: props.labels,
    datasets: props.datasets.map(ds => ({
      ...ds,
      tension: ds.stepped ? 0 : (ds.tension !== undefined ? ds.tension : 0.4), // Smooth curves by default
      pointBackgroundColor: ds.borderColor || '#3B82F6',
      pointBorderColor: '#1A233A',
      pointBorderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6
    }))
  }
})

const defaultOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  plugins: {
    legend: {
      display: true,
      position: 'top',
      labels: {
        color: '#F8FAFC',
        font: { family: "'Inter', sans-serif" },
        usePointStyle: true
      }
    },
    tooltip: {
      backgroundColor: 'rgba(19, 27, 47, 0.9)',
      titleColor: '#F8FAFC',
      bodyColor: '#F8FAFC',
      borderColor: 'rgba(255, 255, 255, 0.1)',
      borderWidth: 1,
      padding: 10,
      cornerRadius: 8,
      callbacks: {
        label: function(context) {
          let label = context.dataset.label || '';
          if (label) {
            label += ': ';
          }
          if (context.parsed.y !== null) {
            label += 'RM' + new Intl.NumberFormat('en-MY', { minimumFractionDigits: 2 }).format(context.parsed.y);
          }
          return label;
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(255, 255, 255, 0.05)',
      },
      ticks: {
        color: '#94A3B8',
        callback: function(value) {
          return 'RM' + value;
        }
      }
    },
    x: {
      grid: {
        display: false
      },
      ticks: {
        color: '#94A3B8'
      }
    }
  }
}

const mergedOptions = computed(() => {
  return { ...defaultOptions, ...props.options }
})
</script>
