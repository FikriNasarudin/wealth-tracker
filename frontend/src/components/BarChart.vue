<template>
  <div style="position: relative; width: 100%; height: 250px;">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'
import { Bar } from 'vue-chartjs'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const props = defineProps({
  labels: {
    type: Array,
    required: true
  },
  data: {
    type: Array,
    required: true
  },
  datasets: {
    type: Array,
    required: false,
    default: null
  }
})

const chartData = computed(() => {
  if (props.datasets) {
    return {
      labels: props.labels,
      datasets: props.datasets
    }
  }
  return {
    labels: props.labels,
    datasets: [
      {
        label: props.label,
        backgroundColor: '#3B82F6', // Vibrant blue
        borderRadius: 4,
        data: props.data
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  plugins: {
    legend: {
      display: computed(() => props.datasets && props.datasets.length > 1).value,
      labels: {
        color: '#F8FAFC'
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
</script>
