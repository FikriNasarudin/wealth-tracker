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
    datasets: props.datasets.map(ds => {
      const baseColor = ds.borderColor || '#3B82F6';
      return {
        ...ds,
        tension: ds.stepped ? 0 : (ds.tension !== undefined ? ds.tension : 0.45),
        pointBackgroundColor: baseColor,
        pointBorderColor: '#0c101b',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: baseColor,
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2,
        fill: ds.fill !== undefined ? ds.fill : true,
        backgroundColor: (context) => {
          const chart = context.chart;
          const {ctx, chartArea} = chart;
          if (!chartArea) return null;
          const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
          
          let colorStart = 'rgba(59, 130, 246, 0.25)';
          if (baseColor === '#10B981' || baseColor === 'var(--success)') {
            colorStart = 'rgba(16, 185, 129, 0.25)';
          } else if (baseColor === '#8B5CF6' || baseColor === 'var(--accent-secondary)') {
            colorStart = 'rgba(139, 92, 246, 0.25)';
          }
          
          gradient.addColorStop(0, colorStart);
          gradient.addColorStop(1, 'rgba(8, 11, 17, 0.01)');
          return gradient;
        }
      }
    })
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
